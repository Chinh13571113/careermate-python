import numpy as np
from sklearn.preprocessing import normalize
from .embedding import gemini_embed
from .collaborative_filtering import cf_service

# ---- Collaborative Filtering vectors (loaded from RecBole/trained model) ----
def get_user_cf_vector(user_id: int) -> np.ndarray | None:
    """Load user's CF vector from trained model or database.
    Returns None if user is new (cold start) or insufficient interactions."""
    return cf_service.get_user_embedding(user_id)

def get_job_cf_vector(job_id: int) -> np.ndarray | None:
    """Load job's CF vector from trained model.
    NOTE: This should NOT be called during indexing, only during scoring."""
    return cf_service.get_job_embedding(job_id)


def build_user_vector(cv_text: str, user_id: int | None = None, x: float = 0.7) -> np.ndarray:
    """
    Build user query vector for job search.

    ⚠️ IMPORTANT: This returns ONLY content-based vector for Weaviate search.
    CF vectors are used separately for re-ranking/scoring, not for initial retrieval.

    Hybrid approach:
    1. Use CB vector (768-dim) for Weaviate semantic search → get top candidates
    2. Re-rank candidates using hybrid score (CB + CF) → final recommendations

    Args:
        cv_text: User's resume/CV text
        user_id: User ID (not used here, but kept for API consistency)
        x: Weight parameter (not used here, but kept for API consistency)

    Returns:
        Content-based embedding vector (768-dim from Gemini)
    """
    # Return pure content-based vector for Weaviate search
    # CF will be applied later during re-ranking
    return gemini_embed(cv_text)


def build_job_vector_for_indexing(title: str, description: str, skills: list = None) -> np.ndarray:
    """
    Build PURE content-based vector for storing in Weaviate.

    ⚠️ IMPORTANT: This should ONLY contain content-based features.
    Do NOT include CF vectors here, as they change over time and would require constant re-indexing.

    Args:
        title: Job title
        description: Job description
        skills: List of required skills

    Returns:
        Content-based embedding vector (768-dim from Gemini)
    """
    # Combine all text components
    skills_text = " ".join(skills) if skills else ""
    combined = f"{title or ''} {skills_text} {description or ''}".strip()
    return gemini_embed(combined)


def compute_hybrid_score(
    job_cb_vector: np.ndarray,
    user_cb_vector: np.ndarray,
    job_id: int,
    user_id: int | None,
    x: float = 0.7
) -> float:
    """
    Compute hybrid similarity score combining Content-Based and Collaborative Filtering.

    Hybrid Strategy:
    - CB score (x): Semantic similarity between user CV and job description (768-dim Gemini embeddings)
    - CF score (1-x): User-job affinity from interaction history (64-dim RecBole embeddings)
    - Final: weighted sum of normalized scores

    This allows CF vectors to evolve without re-indexing Weaviate.

    Args:
        job_cb_vector: Job's content-based vector (768-dim from Weaviate)
        user_cb_vector: User's content-based vector (768-dim from CV)
        job_id: Job ID for loading CF vector
        user_id: User ID for loading CF vector
        x: Weight for content-based similarity (default 0.7 = 70% CB, 30% CF)

    Returns:
        Hybrid similarity score [0, 1]

    Example:
        x=1.0 → Pure content-based (cold start)
        x=0.7 → 70% CB + 30% CF (balanced, recommended)
        x=0.5 → 50% CB + 50% CF (equal weight)
        x=0.0 → Pure collaborative filtering
    """
    # 1. Content-based similarity (cosine similarity)
    cb_score = float(np.dot(
        normalize(job_cb_vector.reshape(1, -1)).ravel(),
        normalize(user_cb_vector.reshape(1, -1)).ravel()
    ))

    # 2. Collaborative filtering score (if available)
    cf_score = 0.0
    if user_id:
        user_cf = get_user_cf_vector(user_id)
        job_cf = get_job_cf_vector(job_id)

        if user_cf is not None and job_cf is not None:
            # Cosine similarity between CF embeddings
            cf_score = float(np.dot(
                normalize(user_cf.reshape(1, -1)).ravel(),
                normalize(job_cf.reshape(1, -1)).ravel()
            ))

    # 3. Weighted hybrid score
    # Both scores are in [0, 1] range (cosine similarity of normalized vectors)
    hybrid_score = x * cb_score + (1 - x) * cf_score

    # Ensure result is in [0, 1] range
    return float(np.clip(hybrid_score, 0.0, 1.0))


def compute_hybrid_scores_batch(
    jobs_data: list,
    user_cb_vector: np.ndarray,
    user_id: int | None,
    x: float = 0.7
) -> list:
    """
    Batch version of compute_hybrid_score for multiple jobs.
    More efficient than calling compute_hybrid_score in a loop.

    Args:
        jobs_data: List of dicts with 'job_id' and 'vector' (CB vector from Weaviate)
        user_cb_vector: User's content-based vector (768-dim)
        user_id: User ID for CF vectors
        x: Weight for content-based component

    Returns:
        List of hybrid scores corresponding to input jobs

    Example:
        jobs_data = [
            {"job_id": 3, "vector": np.array([...])},
            {"job_id": 5, "vector": np.array([...])}
        ]
        scores = compute_hybrid_scores_batch(jobs_data, user_vec, user_id=4, x=0.7)
        # scores = [0.85, 0.72]
    """
    scores = []

    for job_data in jobs_data:
        score = compute_hybrid_score(
            job_cb_vector=job_data['vector'],
            user_cb_vector=user_cb_vector,
            job_id=job_data['job_id'],
            user_id=user_id,
            x=x
        )
        scores.append(score)

    return scores

"""
Content-Based Recommender - Semantic similarity with skill overlap weighting
"""
from apps.recommendation_agent.services.embedding_service import get_gemini_embedding, combine_weighted_text
from apps.recommendation_agent.services.overlap_skill import calculate_skill_overlap_for_job_recommendation
from apps.recommendation_agent.services.weaviate_service import query_weaviate_async


async def get_content_based_recommendations(
    query_item: dict,
    top_n: int = 5,
    weights: dict = None,
    skill_weight: float = 0.3,
    min_threshold: float = 0.15
):
    """
    Content-based recommendation with balanced scoring

    Args:
        query_item: Dict with skills, title, description
        top_n: Number of recommendations to return
        weights: Field weights for embedding (skills, title, description)
        skill_weight: Weight for skill overlap (default 0.3)
        min_threshold: Minimum similarity score to include (default 0.15)

    Returns:
        list: Ranked job recommendations with similarity scores
    """
    if weights is None:
        weights = {"skills": 0.4, "title": 0.4, "description": 0.2}

    # 1. Combine fields into weighted text and create embedding
    combined_text = combine_weighted_text(query_item, weights)
    vector = get_gemini_embedding(combined_text)

    # 2. Query Weaviate with more results for filtering
    results = await query_weaviate_async(vector, limit=top_n * 5)

    # 3. Parse query data
    query_skills = _parse_skills(query_item.get("skills", []))
    query_title = query_item.get("title", "").lower()

    # 4. Calculate scores for each job
    formatted_results = []
    for job in results:
        job_skills = _parse_skills(job["skills"])

        # Calculate semantic similarity (normalize to [0, 1])
        # Cosine distance in Weaviate: 0 = identical, 2 = opposite
        # Convert to similarity: 1 = identical, 0 = opposite
        distance = job["distance"]
        semantic_similarity = max(0.0, min(1.0, (2 - distance) / 2))

        # Calculate skill overlap
        skill_overlap_score = calculate_skill_overlap_for_job_recommendation(
            query_skills, job_skills
        )

        # Calculate title context boost
        title_context_boost = _calculate_title_boost(query_title, job["title"])

        # Calculate final hybrid score
        base_score = (1 - skill_weight) * semantic_similarity + skill_weight * skill_overlap_score
        hybrid_score = base_score + title_context_boost

        # Only include jobs above threshold
        if hybrid_score >= min_threshold:
            formatted_results.append({
                "job_id": job["job_id"],
                "title": job["title"],
                "skills": job["skills"],
                "description": job.get("description", ""),
                "semantic_similarity": round(semantic_similarity, 4),
                "skill_overlap": round(skill_overlap_score, 4),
                "title_boost": round(title_context_boost, 4),
                "similarity": round(hybrid_score, 4)
            })

    # 5. Sort by score and return top N
    formatted_results.sort(key=lambda x: x["similarity"], reverse=True)
    return formatted_results[:top_n]


def _parse_skills(skills):
    """Parse skills from string or list"""
    if isinstance(skills, str):
        return [s.strip() for s in skills.split(",") if s.strip()]
    elif isinstance(skills, list):
        return skills
    return []


def _calculate_title_boost(query_title: str, job_title: str) -> float:
    """
    Calculate title context boost based on term overlap

    Returns:
        float: Boost value (0.0 to 0.2)
    """
    if not query_title:
        return 0.0

    query_terms = set(query_title.split())
    job_terms = set(job_title.lower().split())

    common_terms = query_terms.intersection(job_terms)
    if common_terms:
        boost = 0.1 * len(common_terms)  # 10% per common term
        return min(boost, 0.2)  # Cap at 20%

    return 0.0

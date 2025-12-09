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
    skill_weight: float = 0.5,  # Increase skill importance to 50%
    min_threshold: float = 0.15
):
    """
    Content-based recommendation with balanced scoring

    Args:
        query_item: Dict with skills, title, description
        top_n: Number of recommendations to return
        weights: Field weights for embedding (skills, title, description)
        skill_weight: Weight for skill overlap (default 0.5)
        min_threshold: Minimum similarity score to include (default 0.15)

    Returns:
        list: Ranked job recommendations with similarity scores
    """
    if weights is None:
        # Fixed: weights must sum to 1.0
        weights = {"skills": 0.5, "title": 0.3, "description": 0.2}

    # 1. Combine fields into weighted text and create embedding
    combined_text = combine_weighted_text(query_item, weights)
    vector = get_gemini_embedding(combined_text)

    # 2. Query Weaviate with more results for filtering
    results = await query_weaviate_async(vector, limit=top_n * 5)

    # 3. Parse query data
    query_skills = _parse_skills(query_item.get("skills", []))
    query_title = query_item.get("title", "").lower()

    # Debug logging
    print(f"\n{'='*80}")
    print(f"🔍 CONTENT-BASED RECOMMENDATION DEBUG")
    print(f"{'='*80}")
    print(f"Query Title: {query_title}")
    print(f"Query Skills: {query_skills}")
    print(f"Skill Weight: {skill_weight} (50% semantic + 50% skill)")
    print(f"{'='*80}\n")

    # 4. Calculate scores for each job
    formatted_results = []
    for idx, job in enumerate(results):
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
        # Increase skill importance: 50% semantic + 50% skill (no title boost in base)
        base_score = (1 - skill_weight) * semantic_similarity + skill_weight * skill_overlap_score
        
        # Only add title boost if there's skill match (prevent title-only recommendations)
        if skill_overlap_score > 0:
            hybrid_score = base_score + title_context_boost
        else:
            # Penalize jobs with 0 skill match even if title matches
            hybrid_score = base_score * 0.5  # 50% penalty for no skill match

        # Debug first 3 jobs
        if idx < 3:
            print(f"Job #{idx + 1}: {job['title'][:50]}")
            print(f"  Job Skills: {job_skills[:5]}...")  # Show first 5 skills
            print(f"  Distance: {distance:.4f}")
            print(f"  Semantic: {semantic_similarity:.4f} ({semantic_similarity*100:.1f}%)")
            print(f"  Skill Overlap: {skill_overlap_score:.4f} ({skill_overlap_score*100:.1f}%)")
            print(f"  Title Boost: {title_context_boost:.4f} ({title_context_boost*100:.1f}%)")
            print(f"  Base Score: {base_score:.4f}")
            print(f"  Final Score: {hybrid_score:.4f} ({hybrid_score*100:.1f}%)")
            print(f"  {'⚠️  PENALIZED (no skill match)' if skill_overlap_score == 0 else '✓'}\n")

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
    """Parse skills from string or list and normalize to lowercase"""
    if isinstance(skills, str):
        # Handle comma-separated string
        return [s.strip().lower() for s in skills.split(",") if s.strip()]
    elif isinstance(skills, list):
        # Handle list of strings or dicts
        parsed = []
        for skill in skills:
            if isinstance(skill, str):
                parsed.append(skill.strip().lower())
            elif isinstance(skill, dict):
                # Handle {skill_name: 'Python'} or {name: 'Python'}
                skill_name = skill.get('skill_name') or skill.get('name') or skill.get('skillName')
                if skill_name:
                    parsed.append(str(skill_name).strip().lower())
        return parsed
    return []


def _calculate_title_boost(query_title: str, job_title: str) -> float:
    """
    Calculate title context boost based on term overlap
    Reduced to prevent title from dominating score

    Returns:
        float: Boost value (0.0 to 0.05) - reduced from 0.2
    """
    if not query_title:
        return 0.0

    query_terms = set(query_title.lower().split())  # Normalize to lowercase
    job_terms = set(job_title.lower().split())

    common_terms = query_terms.intersection(job_terms)
    if common_terms:
        boost = 0.02 * len(common_terms)  # 2% per common term (reduced from 10%)
        return min(boost, 0.05)  # Cap at 5% (reduced from 20%)

    return 0.0

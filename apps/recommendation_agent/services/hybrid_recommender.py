"""
Hybrid Recommender - Combines content-based and collaborative filtering
"""
from apps.recommendation_agent.services.content_based_recommender import get_content_based_recommendations
from apps.recommendation_agent.services.collaborative_recommender import get_collaborative_filtering_recommendations


async def get_hybrid_job_recommendations(
    candidate_id: int,
    query_item: dict,
    job_ids: list,
    top_n: int = 5
):
    """
    Hybrid recommendation combining content-based and collaborative filtering

    Args:
        candidate_id: Target user ID
        query_item: Query with skills, title, description
        job_ids: Available job IDs
        top_n: Number of recommendations

    Returns:
        dict: Content-based, collaborative, and hybrid top recommendations
    """
    # 1. Get Content-Based recommendations
    content_results = await get_content_based_recommendations(query_item, top_n=top_n * 2)
    content_scores = {r["job_id"]: r["similarity"] for r in content_results}

    # 2. Try Collaborative Filtering (fallback if insufficient data)
    try:
        cf_results = await get_collaborative_filtering_recommendations(
            candidate_id, job_ids, model=None, n=top_n * 2
        )
        cf_scores = {job["job_id"]: job["similarity"] for job in cf_results}
        has_cf_data = True
    except Exception as e:
        print(f"[⚠️ CF skipped: {e}]")
        cf_results = []
        cf_scores = {}
        has_cf_data = False

    # 3. Set dynamic weights based on data availability
    if not has_cf_data:
        content_weight = 1.0
        cf_weight = 0.0
    else:
        content_weight = 0.8  # Content-based is primary
        cf_weight = 0.2       # CF is secondary

    # 4. Combine scores
    hybrid_combined = {}
    for job_id, c_score in content_scores.items():
        cf_score = cf_scores.get(job_id, 0)
        hybrid_score = (content_weight * c_score) + (cf_weight * cf_score)
        hybrid_combined[job_id] = round(hybrid_score, 4)

    # 5. Rank by hybrid score
    hybrid_ranked = sorted(
        content_results,
        key=lambda x: hybrid_combined.get(x["job_id"], 0),
        reverse=True
    )[:top_n]

    # 6. Attach hybrid score and weights to results
    for r in hybrid_ranked:
        r["final_score"] = hybrid_combined.get(r["job_id"], r["similarity"])
        r["source_weight"] = {"content": content_weight, "cf": cf_weight}

    return {
        "content_based": content_results[:top_n],
        "collaborative": cf_results[:top_n],
        "hybrid_top": hybrid_ranked
    }


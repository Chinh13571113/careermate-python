def calculate_skill_overlap(query_skills: list, job_skills: list) -> float:
    if not query_skills or not job_skills:
        return 0.0

    # Normalize skills to lowercase for comparison
    query_skills_normalized = {str(s).lower().strip() for s in query_skills}
    job_skills_normalized = {str(s).lower().strip() for s in job_skills}

    # Calculate intersection
    overlap = query_skills_normalized.intersection(job_skills_normalized)

    # Calculate Jaccard similarity: |intersection| / |union|
    union = query_skills_normalized.union(job_skills_normalized)
    jaccard_score = len(overlap) / len(union) if union else 0.0

    # Also calculate recall: |intersection| / |job_skills|
    # This measures how many of the required job skills the candidate has
    recall_score = len(overlap) / len(job_skills_normalized) if job_skills_normalized else 0.0

    # Weighted combination (favor recall - having the required skills is more important)
    skill_overlap_score = (0.4 * jaccard_score) + (0.6 * recall_score)

    return skill_overlap_score

def calculate_skill_overlap_for_job_recommendation(user_skills: list, job_skills: list) -> float:
    """
    Tính độ trùng kỹ năng giữa ứng viên (user) và job.

    Logic: Chỉ tính recall_job (user có bao nhiêu % skill job yêu cầu)
    Ứng viên có thêm skill khác KHÔNG bị penalty.
    """
    if not user_skills or not job_skills:
        return 0.0

    # Chuẩn hóa lowercase
    user = {str(s).lower().strip() for s in user_skills if s}
    job = {str(s).lower().strip() for s in job_skills if s}

    overlap = user.intersection(job)
    if not overlap:
        return 0.0

    # Recall: ứng viên cover bao nhiêu % kỹ năng job yêu cầu
    recall_job = len(overlap) / len(job)
    # Chỉ tính recall_job: user cover bao nhiêu % skill job yêu cầu
    # Nếu job cần [python, pandas] và user có [python, pandas, pytorch]
    # → 2/2 = 100% (có đủ yêu cầu, pytorch là bonus không bị trừ điểm)
    # F1-like score

    return recall_job



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
    - user_skills: kỹ năng ứng viên (query)
    - job_skills: kỹ năng trong job posting
    Trả về giá trị [0, 1].
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
    # Precision: bao nhiêu % kỹ năng ứng viên phù hợp job
    recall_user = len(overlap) / len(user)

    # F1-like score
    f1_like = (2 * recall_job * recall_user) / (recall_job + recall_user)
    return round(f1_like, 3)


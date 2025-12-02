"""
Collaborative Filtering Recommender - User-based collaborative filtering with feedback weighting
"""
import os
import pandas as pd
from collections import defaultdict
from asgiref.sync import sync_to_async
from django.conf import settings

# Load job postings CSV for skill data
csv_path = os.path.join(settings.BASE_DIR, 'agent_core', 'data', 'job_postings.csv')
data_jp = pd.read_csv(csv_path, encoding='latin-1')

# Feedback type weights
FEEDBACK_WEIGHTS = {
    'apply': 1.0,   # Strongest signal
    'like': 0.7,    # Medium signal
    'save': 0.5,    # Neutral signal
    'view': 0.3,    # Weak signal
    'dislike': 0.0  # Negative signal
}


def _collaborative_filtering_sync(candidate_id: int, job_ids: list, n: int = 5):
    from apps.recommendation_agent.models import JobFeedback, JobPostings

    print(f"\n🔍 CF Recommendation for Candidate {candidate_id}")

    # 1. Build user-job interaction matrix
    interaction_data = _build_interaction_matrix()
    user_jobs, job_users, user_job_weights = interaction_data

    # Debug: Print interaction matrix stats
    print(f"  Total users with interactions: {len(user_jobs)}")
    print(f"  Total jobs with interactions: {len(job_users)}")

    # 2. Get target user's interactions
    target_user_jobs = user_jobs.get(candidate_id, set())
    if not target_user_jobs:
        print(f"  ⚠️  Candidate {candidate_id} has no interaction history")
        return []

    print(f"  Target user interacted with {len(target_user_jobs)} jobs")

    # 3. Calculate user similarities
    user_similarities = _calculate_user_similarities(
        candidate_id, target_user_jobs, user_jobs, user_job_weights
    )

    if not user_similarities:
        print(f"  ⚠️  No similar users found")
        return []

    # 4. Filter candidate jobs (not yet interacted)
    candidate_jobs = [job_id for job_id in job_ids if job_id not in target_user_jobs]
    if not candidate_jobs:
        print(f"  ⚠️  User has interacted with all available jobs")
        return []

    print(f"  Candidate jobs (not interacted): {len(candidate_jobs)}")

    # 5. Calculate scores for candidate jobs
    job_scores = _calculate_job_scores(candidate_jobs, job_users, user_similarities)

    if not job_scores:
        print(f"  ⚠️  No recommendations found")
        return []

    # 6. Sort and get top N
    sorted_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)[:n]

    # 7. Format results with job details
    return _format_cf_results(sorted_jobs)


def _build_interaction_matrix():
    """Build user-job interaction matrices with weights"""
    from apps.recommendation_agent.models import JobFeedback

    all_feedbacks = JobFeedback.objects.all()
    user_jobs = defaultdict(set)
    job_users = defaultdict(dict)
    user_job_weights = defaultdict(dict)

    print(f"  Processing {all_feedbacks.count()} feedback records...")

    for fb in all_feedbacks:
        # Convert feedback_type to lowercase for case-insensitive matching
        feedback_type_lower = fb.feedback_type.lower() if fb.feedback_type else ''
        feedback_weight = FEEDBACK_WEIGHTS.get(feedback_type_lower, 0.5)

        if fb.score is not None and fb.score > 0:
            weighted_score = fb.score * feedback_weight
        else:
            weighted_score = feedback_weight

        # Skip negative feedback (dislike) from building positive interactions
        if feedback_weight > 0:
            user_jobs[fb.candidate_id].add(fb.job_id)
            job_users[fb.job_id][fb.candidate_id] = weighted_score
            user_job_weights[fb.candidate_id][fb.job_id] = weighted_score

    return user_jobs, job_users, user_job_weights


def _calculate_user_similarities(candidate_id, target_user_jobs, user_jobs, user_job_weights):
    """Calculate weighted Jaccard similarity between users"""
    user_similarities = {}

    for other_user_id, other_user_jobs in user_jobs.items():
        if other_user_id == candidate_id:
            continue

        common_jobs = target_user_jobs.intersection(other_user_jobs)
        if not common_jobs:
            continue

        # Calculate weighted similarity
        common_weight_sum = sum(
            min(
                user_job_weights[candidate_id].get(job_id, 0.5),
                user_job_weights[other_user_id].get(job_id, 0.5)
            )
            for job_id in common_jobs
        )

        all_jobs = target_user_jobs.union(other_user_jobs)
        all_weight_sum = sum(
            max(
                user_job_weights[candidate_id].get(job_id, 0.0),
                user_job_weights[other_user_id].get(job_id, 0.0)
            )
            for job_id in all_jobs
        )

        if all_weight_sum > 0:
            similarity = common_weight_sum / all_weight_sum
            user_similarities[other_user_id] = similarity
            print(f"  Similarity with User {other_user_id}: {similarity:.4f}")

    return user_similarities


def _calculate_job_scores(candidate_jobs, job_users, user_similarities):
    """Calculate weighted scores for candidate jobs"""
    job_scores = {}

    for job_id in candidate_jobs:
        score = 0.0
        users_with_weights = job_users.get(job_id, {})

        for user_id, job_weight in users_with_weights.items():
            if user_id in user_similarities:
                contribution = user_similarities[user_id] * job_weight
                score += contribution

        if score > 0:
            job_scores[job_id] = score

    return job_scores


def _format_cf_results(sorted_jobs):
    """Format CF results with job details and normalized scores"""
    from apps.recommendation_agent.models import JobPostings
    from datetime import date

    predicted_job_ids = [job_id for job_id, _ in sorted_jobs]

    # Only get active, non-expired jobs
    today = date.today()
    jobs = JobPostings.objects.filter(
        id__in=predicted_job_ids,
        status="ACTIVE",
        expiration_date__gte=today
    ).values(
        'id', 'title', 'description', 'address'
    )
    job_details_map = {job['id']: job for job in jobs}

    # Normalize scores
    max_raw_score = sorted_jobs[0][1] if sorted_jobs else 1.0

    detailed_results = []
    for job_id, raw_score in sorted_jobs:
        # Skip if job not found (expired or deleted)
        if job_id not in job_details_map:
            continue

        job_info = job_details_map[job_id]
        normalized_score = raw_score / max_raw_score if max_raw_score > 0 else 0

        # Get skills from CSV
        skills = "N/A"
        try:
            job_row = data_jp[data_jp['id'] == job_id]
            if not job_row.empty:
                skills = job_row.iloc[0].get('skills', 'N/A')
        except Exception:
            pass

        detailed_results.append({
            "job_id": job_id,
            "title": job_info.get('title', 'Unknown'),
            "description": job_info.get('description', '')[:200] + '...' if job_info.get('description', '') else '',
            "skills": skills,
            "similarity": round(normalized_score, 4),
            "raw_cf_score": round(raw_score, 4)
        })

    return detailed_results


async def get_collaborative_filtering_recommendations(candidate_id: int, job_ids: list, model=None, n: int = 5):
    """Async wrapper for collaborative filtering"""
    return await sync_to_async(_collaborative_filtering_sync)(candidate_id, job_ids, n)

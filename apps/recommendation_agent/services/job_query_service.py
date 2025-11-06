"""
Job Query Service - Handles database queries for job postings
"""
from asgiref.sync import sync_to_async
from apps.recommendation_agent.models import JobPostings


def _query_all_jobs_sync():
    """
    Get ACTIVE jobs from PostgreSQL (ORM)

    Returns:
        list: List of active job postings
    """
    jobs = JobPostings.objects.filter(status="ACTIVE").values(
        "id", "title", "description", "address"
    )

    job_list = [
        {
            "job_id": job["id"],
            "title": job["title"],
            "description": job["description"],
            "address": job["address"]
        }
        for job in jobs
    ]
    return job_list


def query_all_jobs():
    """
    Get active jobs (synchronous wrapper for backward compatibility)

    Returns:
        list: List of active job postings
    """
    return _query_all_jobs_sync()


async def query_all_jobs_async():
    """
    Get active jobs (async wrapper)

    Returns:
        list: List of active job postings
    """
    return await sync_to_async(_query_all_jobs_sync)()


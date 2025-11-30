"""
Job Query Service - Handles database queries for job postings
"""
from datetime import date
from asgiref.sync import sync_to_async
from apps.recommendation_agent.models import JobPostings


def _query_all_jobs_sync():
    """
    Get ACTIVE and non-expired jobs from PostgreSQL (ORM)

    Returns:
        list: List of active job postings that haven't expired
    """
    today = date.today()
    jobs = JobPostings.objects.filter(
        status="ACTIVE",
        expiration_date__gte=today
    ).values(
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
    Get active and non-expired jobs (synchronous wrapper for backward compatibility)

    Returns:
        list: List of active job postings that haven't expired
    """
    return _query_all_jobs_sync()


async def query_all_jobs_async():
    """
    Get active and non-expired jobs (async wrapper)

    Returns:
        list: List of active job postings that haven't expired
    """
    return await sync_to_async(_query_all_jobs_sync)()

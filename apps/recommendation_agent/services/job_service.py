"""
Service to fetch jobs from PostgreSQL and index them into Weaviate
"""
from typing import List, Optional
from django.db.models import QuerySet
from django.db import connections
from apps.recommendation_agent.models import JobPostings
from .hybrid_builder import build_job_vector_for_indexing
from .weaviate_service import index_job, ensure_schema
import logging

logger = logging.getLogger(__name__)


class JobIndexingService:
    """Service to sync jobs from PostgreSQL to Weaviate"""

    @staticmethod
    def fetch_jobs_from_postgres(
        limit: Optional[int] = None,
        only_active: bool = True,
        job_ids: Optional[List[int]] = None
    ) -> QuerySet:
        """
        Fetch jobs from PostgreSQL database.

        Args:
            limit: Maximum number of jobs to fetch
            only_active: Only fetch approved/active jobs
            job_ids: Specific job IDs to fetch (optional)

        Returns:
            QuerySet of Job objects
        """
        queryset = JobPostings.objects.using('postgres').select_related('recruiter')

        if only_active:
            queryset = queryset.filter(status='approved')

        if job_ids:
            queryset = queryset.filter(id__in=job_ids)

        if limit:
            queryset = queryset[:limit]

        return queryset

    @staticmethod
    def get_job_skills(job_id: int) -> List[str]:
        """
        Fetch skills for a job from job_descriptions and jd_skills tables.

        Args:
            job_id: Job posting ID

        Returns:
            List of skill names
        """
        # noinspection SqlResolve
        skills_query = """
            SELECT s.name 
            FROM job_descriptions jd
            JOIN jd_skills s ON jd.skill_id = s.id
            WHERE jd.job_posting_id = %s
        """

        skills = []
        try:
            with connections['postgres'].cursor() as cursor:
                cursor.execute(skills_query, [job_id])
                skills = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.warning(f"Could not fetch skills for job {job_id}: {e}")

        return skills

    @classmethod
    def index_single_job(cls, job: JobPostings) -> bool:
        """
        Index a single job into Weaviate.

        Args:
            job: Job model instance

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare job data
            title = job.title or ""
            description = job.description or ""
            address = job.address or ""
            status = job.status or "approved"
            company_name = job.recruiter.company_name if job.recruiter else "Unknown Company"
            created_at = str(job.created_at) if job.created_at else ""

            # Fetch skills from database
            skills = cls.get_job_skills(job.id)

            # Generate content-based vector
            vector = build_job_vector_for_indexing(title, description, skills)

            # Index into Weaviate
            index_job(
                job_id=job.id,
                title=title,
                description=description,
                address=address,
                status=status,
                company_name=company_name,
                skills=skills,
                created_at=created_at,
                vector=vector.tolist()
            )

            logger.info(f"Successfully indexed job {job.id}: {job.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to index job {job.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    @classmethod
    def bulk_index_jobs(
        cls,
        limit: Optional[int] = None,
        only_active: bool = True,
        job_ids: Optional[List[int]] = None
    ) -> dict:
        """
        Bulk index jobs from PostgreSQL to Weaviate.

        Args:
            limit: Maximum number of jobs to index
            only_active: Only index approved jobs
            job_ids: Specific job IDs to index

        Returns:
            Dictionary with success/failure counts
        """
        # Ensure Weaviate schema exists
        ensure_schema()

        # Fetch jobs from PostgreSQL
        jobs = cls.fetch_jobs_from_postgres(limit, only_active, job_ids)

        success_count = 0
        failure_count = 0
        failed_jobs = []

        total = jobs.count()
        logger.info(f"Starting to index {total} jobs into Weaviate...")

        for idx, job in enumerate(jobs, 1):
            if cls.index_single_job(job):
                success_count += 1
            else:
                failure_count += 1
                failed_jobs.append(job.id)

            # Progress logging every 10 jobs
            if idx % 10 == 0:
                logger.info(f"Progress: {idx}/{total} jobs processed")

        result = {
            "total": total,
            "success": success_count,
            "failed": failure_count,
            "failed_job_ids": failed_jobs
        }

        logger.info(f"Indexing complete: {success_count} succeeded, {failure_count} failed")
        return result

    @staticmethod
    def get_job_by_id(job_id: int) -> Optional[JobPostings]:
        """
        Fetch a single job from PostgreSQL by ID.

        Args:
            job_id: Job ID to fetch

        Returns:
            Job instance or None if not found
        """
        try:
            return JobPostings.objects.using('postgres').select_related('recruiter').get(id=job_id)
        except JobPostings.DoesNotExist:
            logger.warning(f"Job {job_id} not found in PostgreSQL")
            return None

    @classmethod
    def sync_single_job_to_weaviate(cls, job_id: int) -> bool:
        """
        Sync a single job from PostgreSQL to Weaviate.
        Useful for real-time updates when a job is created/updated.

        Handles:
        - New approved jobs: Index to Weaviate
        - Updated approved jobs: Re-index to Weaviate (no duplicates)
        - Non-approved jobs: Remove from Weaviate if exists
        - Deleted jobs: Remove from Weaviate if exists

        Args:
            job_id: Job ID to sync

        Returns:
            True if successful, False otherwise
        """
        from .weaviate_service import delete_job

        try:
            # Try to fetch job from PostgreSQL
            job = cls.get_job_by_id(job_id)

            if job is None:
                # Job doesn't exist in PostgreSQL - remove from Weaviate if present
                logger.info(f"Job {job_id} not found in PostgreSQL, removing from Weaviate if exists")
                delete_job(job_id)
                return True

            if job.status == 'approved':
                # Job is approved - index/update in Weaviate
                logger.info(f"Syncing approved job {job_id} to Weaviate: '{job.title}'")
                success = cls.index_single_job(job)
                if success:
                    logger.info(f"✓ Successfully synced job {job_id}")
                else:
                    logger.error(f"✗ Failed to sync job {job_id}")
                return success
            else:
                # Job exists but not approved - remove from Weaviate if present
                logger.info(f"Job {job_id} status is '{job.status}', removing from Weaviate if exists")
                delete_job(job_id)
                return True

        except Exception as e:
            logger.error(f"Exception while syncing job {job_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

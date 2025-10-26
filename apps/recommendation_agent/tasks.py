"""
Celery tasks for periodic sync between PostgreSQL and Weaviate
Detects changes made directly in the database (bypassing Django ORM)
"""
from celery import shared_task
from django.db import connections
from apps.recommendation_agent.models import JobPostings
from apps.recommendation_agent.services.job_service import JobIndexingService
from apps.recommendation_agent.services.weaviate_service import delete_job, get_client
import weaviate.classes as wvc
import logging

logger = logging.getLogger(__name__)


@shared_task
def periodic_sync_jobs():
    """
    Periodic task to sync all jobs between PostgreSQL and Weaviate
    Detects:
    - New jobs added directly to DB
    - Jobs updated directly in DB
    - Jobs deleted directly from DB
    - Status changes
    """
    logger.info("🔄 Starting periodic sync: PostgreSQL → Weaviate")

    try:
        # Get all approved jobs from PostgreSQL
        postgres_jobs = JobPostings.objects.using('postgres').filter(status='approved').values_list('id', flat=True)
        postgres_job_ids = set(postgres_jobs)
        logger.info(f"📊 PostgreSQL: {len(postgres_job_ids)} approved jobs")

        # Get all jobs from Weaviate
        with get_client() as client:
            collection = client.collections.get("JobPosting")
            response = collection.query.fetch_objects(limit=10000)
            weaviate_job_ids = {obj.properties.get("job_id") for obj in response.objects}
            logger.info(f"📊 Weaviate: {len(weaviate_job_ids)} jobs")

        # Find differences
        jobs_to_add = postgres_job_ids - weaviate_job_ids  # In PostgreSQL but not in Weaviate
        jobs_to_remove = weaviate_job_ids - postgres_job_ids  # In Weaviate but not in PostgreSQL
        jobs_to_check = postgres_job_ids & weaviate_job_ids  # In both (check for updates)

        stats = {
            "added": 0,
            "removed": 0,
            "updated": 0,
            "checked": 0,
            "errors": 0
        }

        # Add missing jobs
        if jobs_to_add:
            logger.info(f"➕ Adding {len(jobs_to_add)} new jobs to Weaviate")
            for job_id in jobs_to_add:
                try:
                    if JobIndexingService.sync_single_job_to_weaviate(job_id):
                        stats["added"] += 1
                    else:
                        stats["errors"] += 1
                except Exception as e:
                    logger.error(f"Error adding job {job_id}: {e}")
                    stats["errors"] += 1

        # Remove deleted jobs
        if jobs_to_remove:
            logger.info(f"➖ Removing {len(jobs_to_remove)} deleted jobs from Weaviate")
            for job_id in jobs_to_remove:
                try:
                    delete_job(job_id)
                    stats["removed"] += 1
                except Exception as e:
                    logger.error(f"Error removing job {job_id}: {e}")
                    stats["errors"] += 1

        # Check for updates in existing jobs (sample check)
        if jobs_to_check:
            # Only check a sample to avoid overload (e.g., 10% or recently modified)
            sample_size = min(len(jobs_to_check), max(10, len(jobs_to_check) // 10))
            sample_jobs = list(jobs_to_check)[:sample_size]

            logger.info(f"🔍 Checking {sample_size} jobs for updates")

            for job_id in sample_jobs:
                try:
                    # Get job from PostgreSQL
                    job = JobPostings.objects.using('postgres').get(id=job_id)

                    # Get job from Weaviate
                    with get_client() as client:
                        collection = client.collections.get("JobPosting")
                        response = collection.query.fetch_objects(
                            filters=wvc.query.Filter.by_property("job_id").equal(job_id),
                            limit=1
                        )

                        if len(response.objects) > 0:
                            weaviate_job = response.objects[0].properties

                            # Check if title or description changed
                            if (weaviate_job.get("title") != job.title or
                                weaviate_job.get("description") != job.description):
                                logger.info(f"📝 Job {job_id} has updates, re-syncing")
                                JobIndexingService.sync_single_job_to_weaviate(job_id)
                                stats["updated"] += 1

                        stats["checked"] += 1

                except Exception as e:
                    logger.error(f"Error checking job {job_id}: {e}")
                    stats["errors"] += 1

        # Log summary
        logger.info(
            f"✅ Periodic sync complete: "
            f"Added={stats['added']}, "
            f"Removed={stats['removed']}, "
            f"Updated={stats['updated']}, "
            f"Checked={stats['checked']}, "
            f"Errors={stats['errors']}"
        )

        return stats

    except Exception as e:
        logger.error(f"❌ Periodic sync failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@shared_task
def detect_db_changes():
    """
    Detect changes in PostgreSQL by checking updated_at timestamps
    More efficient than full sync - only checks recently modified records

    Note: Requires 'updated_at' column in job_postings table
    """
    logger.info("🔍 Detecting recent database changes")

    try:
        # Check for jobs modified in last 5 minutes
        from datetime import datetime, timedelta

        # Note: This requires an 'updated_at' or 'modified_at' column
        # If you don't have it, use periodic_sync_jobs instead

        with connections['postgres'].cursor() as cursor:
            # Check if updated_at column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='job_postings' 
                AND column_name IN ('updated_at', 'modified_at')
            """)

            has_timestamp = cursor.fetchone()

            if not has_timestamp:
                logger.warning("⚠️ No timestamp column found. Use periodic_sync_jobs instead.")
                return {"error": "No timestamp column"}

            timestamp_col = has_timestamp[0]
            five_mins_ago = datetime.now() - timedelta(minutes=5)

            cursor.execute(f"""
                SELECT id FROM job_postings 
                WHERE {timestamp_col} >= %s
            """, [five_mins_ago])

            modified_job_ids = [row[0] for row in cursor.fetchall()]

            if modified_job_ids:
                logger.info(f"📝 Found {len(modified_job_ids)} recently modified jobs")

                for job_id in modified_job_ids:
                    JobIndexingService.sync_single_job_to_weaviate(job_id)

                return {"synced": len(modified_job_ids)}
            else:
                logger.info("✅ No recent changes detected")
                return {"synced": 0}

    except Exception as e:
        logger.error(f"❌ Error detecting changes: {e}")
        return {"error": str(e)}


@shared_task
def full_resync():
    """
    Full resynchronization - reindex all approved jobs
    Use this when you want to ensure complete data consistency
    """
    logger.info("🔄 Starting FULL resynchronization")

    try:
        result = JobIndexingService.bulk_index_jobs(only_active=True)

        logger.info(
            f"✅ Full resync complete: "
            f"Total={result['total']}, "
            f"Success={result['success']}, "
            f"Failed={result['failed']}"
        )

        return result

    except Exception as e:
        logger.error(f"❌ Full resync failed: {e}")
        return {"error": str(e)}


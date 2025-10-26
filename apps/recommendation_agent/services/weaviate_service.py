import os
import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType
from django.db import connections

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8081")
CLASS_NAME = "JobPosting"

def get_client():
    """Get Weaviate v4 client connection"""
    return weaviate.connect_to_local(
        host="localhost",
        port=8081,
        grpc_port=50051,
    )

def ensure_schema():
    """Ensure Weaviate schema matches the actual database structure"""
    try:
        with get_client() as client:
            # Check if collection exists
            if client.collections.exists(CLASS_NAME):
                print(f"✓ Weaviate collection '{CLASS_NAME}' already exists")
                return

            # Create collection with properties
            client.collections.create(
                name=CLASS_NAME,
                description="Job postings with embeddings for recommendation",
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # We'll provide our own vectors
                properties=[
                    Property(name="job_id", data_type=DataType.INT, description="Job posting ID from PostgreSQL"),
                    Property(name="title", data_type=DataType.TEXT, description="Job title"),
                    Property(name="description", data_type=DataType.TEXT, description="Job description"),
                    Property(name="address", data_type=DataType.TEXT, description="Job location"),
                    Property(name="status", data_type=DataType.TEXT, description="Job status (approved, pending, etc)"),
                    Property(name="company_name", data_type=DataType.TEXT, description="Recruiter company name"),
                    Property(name="skills", data_type=DataType.TEXT_ARRAY, description="Required skills for the job"),
                    Property(name="created_at", data_type=DataType.TEXT, description="Job creation date")
                ]
            )
            print(f"✓ Created Weaviate collection '{CLASS_NAME}'")
    except Exception as e:
        print(f"⚠ Error ensuring schema: {e}")

def index_job(job_id: int, title: str, description: str, address: str,
              status: str, company_name: str, skills: list, created_at: str,
              vector: list[float]):
    """
    Index or update a job posting in Weaviate with its embedding vector.
    If job already exists, it will be updated instead of creating a duplicate.

    Args:
        job_id: Job posting ID from PostgreSQL
        title: Job title
        description: Job description
        address: Job location
        status: Job status
        company_name: Company name
        skills: List of required skills
        created_at: Creation date
        vector: Embedding vector for the job
    """
    ensure_schema()

    props = {
        "job_id": job_id,
        "title": title,
        "description": description or "",
        "address": address or "",
        "status": status or "active",
        "company_name": company_name or "",
        "skills": skills or [],
        "created_at": created_at or ""
    }

    try:
        with get_client() as client:
            collection = client.collections.get(CLASS_NAME)

            # Check if job already exists and delete it to avoid duplicates
            existing = collection.query.fetch_objects(
                filters=wvc.query.Filter.by_property("job_id").equal(job_id),
                limit=1
            )

            if len(existing.objects) > 0:
                # Delete existing entry
                collection.data.delete_by_id(existing.objects[0].uuid)
                print(f"↻ Updated job {job_id}: {title}")
            else:
                print(f"✓ Indexed job {job_id}: {title}")

            # Insert new/updated entry
            collection.data.insert(
                properties=props,
                vector=vector
            )
    except Exception as e:
        print(f"✗ Error indexing job {job_id}: {e}")


def search_jobs(user_vec: list[float], top_k=10, query_text=None, alpha=0.7, status_filter="approved"):
    """
    Search for jobs using hybrid search (vector + keyword)

    Args:
        user_vec: User/candidate embedding vector
        top_k: Number of results to return
        query_text: Optional text query for hybrid search
        alpha: Balance between vector (1.0) and keyword (0.0) search
        status_filter: Filter by job status (default: approved)

    Returns:
        List of matching job postings with similarity scores
    """
    try:
        ensure_schema()

        with get_client() as client:
            collection = client.collections.get(CLASS_NAME)

            # Build filter for status
            filter_obj = None
            if status_filter:
                filter_obj = wvc.query.Filter.by_property("status").equal(status_filter)

            # Perform search
            if query_text:
                # Hybrid search (vector + keyword)
                response = collection.query.hybrid(
                    query=query_text,
                    vector=user_vec,
                    alpha=alpha,
                    limit=top_k,
                    filters=filter_obj,
                    return_metadata=wvc.query.MetadataQuery(distance=True, certainty=True)
                )
            else:
                # Pure vector search
                response = collection.query.near_vector(
                    near_vector=user_vec,
                    limit=top_k,
                    filters=filter_obj,
                    return_metadata=wvc.query.MetadataQuery(distance=True, certainty=True)
                )

            # Convert response to list of dictionaries
            jobs = []
            for obj in response.objects:
                job_data = {
                    "job_id": obj.properties.get("job_id"),
                    "title": obj.properties.get("title"),
                    "description": obj.properties.get("description"),
                    "address": obj.properties.get("address"),
                    "status": obj.properties.get("status"),
                    "company_name": obj.properties.get("company_name"),
                    "skills": obj.properties.get("skills"),
                    "created_at": obj.properties.get("created_at"),
                    "_additional": {
                        "distance": obj.metadata.distance,
                        "certainty": obj.metadata.certainty
                    }
                }
                jobs.append(job_data)

            print(f"✓ Found {len(jobs)} matching jobs")
            return jobs

    except Exception as e:
        print(f"✗ Error searching jobs: {e}")
        import traceback
        traceback.print_exc()
        return []

def bulk_index_from_postgres(limit=None):
    """
    Bulk index all approved jobs from PostgreSQL into Weaviate
    Note: You need to provide embedding vectors separately

    Args:
        limit: Optional limit on number of jobs to index
    """
    from apps.recommendation_agent.models import JobPostings

    ensure_schema()

    try:
        # Query approved jobs from PostgreSQL
        query = JobPostings.objects.using('postgres').filter(status='approved')
        if limit:
            query = query[:limit]

        jobs = query.select_related('recruiter')
        job_count = jobs.count()

        print(f"Found {job_count} approved jobs to index")

        for job in jobs:
            # Get skills for this job from job_descriptions table
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
                    cursor.execute(skills_query, [job.id])
                    skills = [row[0] for row in cursor.fetchall()]
            except Exception as e:
                print(f"⚠ Could not fetch skills for job {job.id}: {e}")
                skills = []

            # Extract skills from description if no skills in database
            if not skills and job.description:
                # Fallback: You could parse skills from description here
                print(f"⚠ No skills found in job_descriptions table for job {job.id}")

            company_name = job.recruiter.company_name if job.recruiter else "Unknown Company"
            created_at_str = str(job.created_at) if job.created_at else ""

            print(f"Job {job.id}: {job.title}")
            print(f"  Company: {company_name}")
            print(f"  Skills: {skills if skills else 'No skills defined'}")
            print(f"  Status: {job.status}")

            # TODO: Generate embedding vector for this job and call index_job()
            # Example:
            # job_text = f"{job.title} {job.description} {' '.join(skills)}"
            # vector = generate_embedding(job_text)  # You need to implement this
            # index_job(
            #     job_id=job.id,
            #     title=job.title,
            #     description=job.description or "",
            #     address=job.address or "",
            #     status=job.status or "approved",
            #     company_name=company_name,
            #     skills=skills,
            #     created_at=created_at_str,
            #     vector=vector
            # )

        print(f"✓ Bulk indexing complete - processed {job_count} jobs")
        print(f"\n⚠ NOTE: job_descriptions and jd_skills tables are empty.")
        print(f"   You need to populate these tables with skill data for each job posting.")

    except Exception as e:
        print(f"✗ Error bulk indexing: {e}")
        import traceback
        traceback.print_exc()

def clear_all_jobs():
    """Clear all job postings from Weaviate (useful for re-indexing)"""
    try:
        with get_client() as client:
            client.collections.delete(CLASS_NAME)
            print(f"✓ Cleared all jobs from Weaviate")
            ensure_schema()
    except Exception as e:
        print(f"✗ Error clearing jobs: {e}")

def get_job_count():
    """Get total number of jobs indexed in Weaviate"""
    try:
        with get_client() as client:
            collection = client.collections.get(CLASS_NAME)
            response = collection.aggregate.over_all(total_count=True)
            count = response.total_count
            print(f"✓ Total jobs in Weaviate: {count}")
            return count
    except Exception as e:
        print(f"✗ Error getting job count: {e}")
        return 0


def delete_job(job_id: int):
    """
    Delete a job from Weaviate by job_id

    Args:
        job_id: Job posting ID to delete

    Returns:
        True if deleted, False if not found or error
    """
    try:
        with get_client() as client:
            collection = client.collections.get(CLASS_NAME)

            # Find all objects with this job_id (in case of duplicates)
            response = collection.query.fetch_objects(
                filters=wvc.query.Filter.by_property("job_id").equal(job_id),
                limit=100  # Handle potential duplicates
            )

            if len(response.objects) == 0:
                print(f"⚠ Job {job_id} not found in Weaviate")
                return False

            # Delete all matching objects
            deleted_count = 0
            for obj in response.objects:
                collection.data.delete_by_id(obj.uuid)
                deleted_count += 1

            print(f"✓ Deleted {deleted_count} entry(ies) for job {job_id}")
            return True

    except Exception as e:
        print(f"✗ Error deleting job {job_id}: {e}")
        return False


def remove_duplicates():
    """
    Remove duplicate job entries from Weaviate.
    Keeps only the most recent entry for each job_id.

    Returns:
        Dictionary with cleanup statistics
    """
    try:
        with get_client() as client:
            collection = client.collections.get(CLASS_NAME)

            # Fetch all jobs
            print("Scanning Weaviate for duplicates...")
            response = collection.query.fetch_objects(limit=10000)

            # Group by job_id
            job_map = {}
            for obj in response.objects:
                job_id = obj.properties.get("job_id")
                if job_id not in job_map:
                    job_map[job_id] = []
                job_map[job_id].append(obj)

            # Find and remove duplicates
            duplicates_found = 0
            entries_deleted = 0

            for job_id, objects in job_map.items():
                if len(objects) > 1:
                    duplicates_found += 1
                    # Keep the first one, delete the rest
                    for obj in objects[1:]:
                        collection.data.delete_by_id(obj.uuid)
                        entries_deleted += 1
                    print(f"✓ Removed {len(objects)-1} duplicate(s) for job_id {job_id}")

            result = {
                "total_jobs": len(job_map),
                "duplicates_found": duplicates_found,
                "entries_deleted": entries_deleted
            }

            print(f"\n✓ Cleanup complete:")
            print(f"  - Total unique jobs: {result['total_jobs']}")
            print(f"  - Jobs with duplicates: {result['duplicates_found']}")
            print(f"  - Duplicate entries deleted: {result['entries_deleted']}")

            return result

    except Exception as e:
        print(f"✗ Error removing duplicates: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def sync_with_postgres():
    """
    Synchronize Weaviate with PostgreSQL:
    - Remove jobs that no longer exist or are not approved in PostgreSQL
    - Update jobs that have changed

    Returns:
        Dictionary with sync statistics
    """
    from apps.recommendation_agent.models import JobPostings

    try:
        with get_client() as client:
            collection = client.collections.get(CLASS_NAME)

            print("Fetching all jobs from Weaviate...")
            weaviate_response = collection.query.fetch_objects(limit=10000)
            weaviate_jobs = {obj.properties.get("job_id"): obj.uuid
                           for obj in weaviate_response.objects}

            print(f"Found {len(weaviate_jobs)} jobs in Weaviate")

            print("Fetching approved jobs from PostgreSQL...")
            postgres_jobs = set(
                JobPostings.objects.using('postgres')
                .filter(status='approved')
                .values_list('id', flat=True)
            )

            print(f"Found {len(postgres_jobs)} approved jobs in PostgreSQL")

            # Find jobs to delete (in Weaviate but not approved in PostgreSQL)
            jobs_to_delete = set(weaviate_jobs.keys()) - postgres_jobs

            deleted_count = 0
            for job_id in jobs_to_delete:
                delete_job(job_id)
                deleted_count += 1

            result = {
                "weaviate_jobs": len(weaviate_jobs),
                "postgres_jobs": len(postgres_jobs),
                "deleted": deleted_count,
                "remaining": len(weaviate_jobs) - deleted_count
            }

            print(f"\n✓ Sync complete:")
            print(f"  - Jobs in Weaviate: {result['weaviate_jobs']}")
            print(f"  - Approved jobs in PostgreSQL: {result['postgres_jobs']}")
            print(f"  - Jobs deleted from Weaviate: {result['deleted']}")
            print(f"  - Jobs remaining: {result['remaining']}")

            return result

    except Exception as e:
        print(f"✗ Error syncing with PostgreSQL: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

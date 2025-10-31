import asyncio

from agent_core.weaviate_config import WeaviateClientManager

manager = WeaviateClientManager()
client = manager.get_client()
def _query_weaviate_sync(vector, limit):
    """Synchronous function to query Weaviate using v4 API with default vector"""
    # Get the collection
    job_collection = client.collections.get("JobPosting")

    # Query using v4 API with default vector (no target_vector needed)
    response = job_collection.query.near_vector(
        near_vector=vector,
        limit=limit,
        return_metadata=['distance'],
        include_vector=True
    )

    items = []
    for obj in response.objects:
        skills_field = obj.properties.get("skills", [])
        # nếu skills là list, nối thành chuỗi
        if isinstance(skills_field, list):
            skills_text = ", ".join(str(s) for s in skills_field)
        else:
            skills_text = str(skills_field)

        items.append({
            "job_id": obj.properties.get("jobId"),
            "title": obj.properties.get("title"),
            "skills": skills_text,
            "address": obj.properties.get("address"),
            "description": obj.properties.get("description"),
            "distance": obj.metadata.distance if obj.metadata else 0,
        })
    return items

async def query_weaviate_async(vector: list, limit: int = 10):
    """Async wrapper to query Weaviate"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _query_weaviate_sync, vector, limit)


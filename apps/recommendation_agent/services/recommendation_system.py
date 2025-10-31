import asyncio

import numpy as np
import pandas as pd
import os
import django
import sys

from dotenv import load_dotenv
from google import genai
from apps.recommendation_agent.services.weaviate_service import query_weaviate_async, manager
from apps.recommendation_agent.services.overlap_skill import calculate_skill_overlap

load_dotenv()
# Setup Django environment FIRST before importing models
django_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(django_base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

# NOW import Django models after setup
from django.conf import settings
from apps.recommendation_agent.models import Candidate

# Get the correct path to the CSV file
csv_path = os.path.join(settings.BASE_DIR, 'agent_core', 'data', 'job_postings.csv')
data_jp = pd.read_csv(csv_path, encoding='latin-1')

#get data from postgres by candidateId
def get_candidate_by_id(candidate_id: int, resume_id: int | None = None) -> dict | None:
    """
    Get candidate by ID with their title and skills from resume(s).

    Args:
        candidate_id: The ID of the candidate
        resume_id: Optional - If provided, only return this specific resume. If None, return all resumes.

    Returns:
        Dictionary with candidate title and skills from specified resume(s), or None if not found
    """
    try:
        candidate = (
            Candidate.objects
            .select_related('account')
            .prefetch_related('resumes__skills')
            .get(candidate_id=candidate_id)
        )

        resumes_data = []
        # The 'resumes' relationship exists via Resume model's related_name='resumes'
        # IDE may show warning because Candidate has managed=False, but it works at runtime
        all_resumes = candidate.resumes.all().order_by('-created_at')  # type: ignore

        # If resume_id is provided, filter to get only that specific resume
        if resume_id is not None:
            all_resumes = all_resumes.filter(resume_id=resume_id)
            if not all_resumes.exists():
                return None  # Resume not found for this candidate

        for resume in all_resumes:
            skills = []
            for skill in resume.skills.all():
                skills.append({
                    "skill_id": skill.skill_id,
                    "skill_name": skill.skill_name,
                    "yearOfExperience": skill.year_of_experience or 0
                })

            resumes_data.append({
                "title": candidate.title or "",
                "resume_id": resume.resume_id,
                "skills": skills,
                "skills_count": len(skills)
            })

        return {
            "candidate_id": candidate.candidate_id,
            "title": candidate.title or "",
            "resumes": resumes_data,
        }
    except Candidate.DoesNotExist:
        return None

#init weaviate
# Initialize Gemini client
gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_embedding(text: str):
    """Tạo vector embedding bằng Gemini (models/embedding-001)"""
    text = (text or "").strip()
    if not text:
        return None

    response = gemini_client.models.embed_content(
        model="models/embedding-001",
        contents=text
    )

    # Trả về list[float] (Weaviate yêu cầu dạng này)
    return np.array(response.embeddings[0].values, dtype=np.float32).tolist()


# model = SentenceTransformer("all-MiniLM-L6-v2")
# manager = WeaviateClientManager()
# client = manager.get_client()

#content-based
#async query to weaviate
# def _query_weaviate_sync(vector, limit):
#     """Synchronous function to query Weaviate using v4 API with default vector"""
#     # Get the collection
#     job_collection = client.collections.get("JobPosting")
#
#     # Query using v4 API with default vector (no target_vector needed)
#     response = job_collection.query.near_vector(
#         near_vector=vector,
#         limit=limit,
#         return_metadata=['distance'],
#         include_vector=True
#     )
#
#     items = []
#     for obj in response.objects:
#         skills_field = obj.properties.get("skills", [])
#         # nếu skills là list, nối thành chuỗi
#         if isinstance(skills_field, list):
#             skills_text = ", ".join(str(s) for s in skills_field)
#         else:
#             skills_text = str(skills_field)
#
#         items.append({
#             "job_id": obj.properties.get("jobId"),
#             "title": obj.properties.get("title"),
#             "skills": skills_text,
#             "address": obj.properties.get("address"),
#             "description": obj.properties.get("description"),
#             "distance": obj.metadata.distance if obj.metadata else 0,
#         })
#     return items
#
# async def query_weaviate_async(vector: list, limit: int = 10):
#     """Async wrapper to query Weaviate"""
#     loop = asyncio.get_running_loop()
#     return await loop.run_in_executor(None, _query_weaviate_sync, vector, limit)




# fetch job posting from weaviate
 # compare title, skills, address
 #return top k job postings score similarity

#Content-Based Recommendation with Skill Overlap Weighting
async def get_content_based_recommendations(query_item, top_n=5, weights=None, skill_weight=0.4):
    if weights is None:
        weights = {"skills": 0.5, "title": 0.3, "description": 0.15}

    # 1️⃣ Combine all fields into weighted text
    def to_text(v):
        if isinstance(v, list):
            return ", ".join(str(x) for x in v)
        return str(v or "")

    # Create weighted combined text (repeat important fields to increase their weight)
    skills_text = to_text(query_item.get("skills", ""))
    title_text = to_text(query_item.get("title", ""))
    description_text = to_text(query_item.get("description", ""))

    # Combine with weights by repeating (simple but effective approach)
    combined_parts = []
    if skills_text:
        combined_parts.extend([skills_text] * 10)  # High weight for skills
    if title_text:
        combined_parts.extend([title_text] * 3)  # Medium weight for title
    if description_text:
        combined_parts.append(description_text)  # Low weight for description

    combined_text = " ".join(combined_parts)

    # 2️⃣ Create single embedding
    # embedding = model.encode(combined_text, normalize_embeddings=True)
    # vector = embedding.tolist()
    vector = get_gemini_embedding(combined_text)
    # 3️⃣ Query Weaviate with single vector (get more results for better filtering)
    results = await query_weaviate_async(vector, limit=top_n * 3)  # Get 3x more for skill filtering

    # 4️⃣ Calculate hybrid scores combining semantic similarity + skill overlap
    query_skills = query_item.get("skills", [])
    if isinstance(query_skills, str):
        query_skills = [s.strip() for s in query_skills.split(",")]

    formatted_results = []
    for job in results:
        # Parse job skills
        job_skills_text = job["skills"]
        if isinstance(job_skills_text, str):
            job_skills = [s.strip() for s in job_skills_text.split(",") if s.strip()]
        else:
            job_skills = []

        # Calculate semantic similarity (from vector distance)
        semantic_similarity = 1 - job["distance"]

        # Calculate skill overlap score
        skill_overlap_score = calculate_skill_overlap(query_skills, job_skills)

        # Hybrid score: weighted combination
        hybrid_score = (1 - skill_weight) * semantic_similarity + skill_weight * skill_overlap_score

        formatted_results.append({
            "job_id": job["job_id"],
            "title": job["title"],
            "skills": job["skills"],
            "description": job.get("description", ""),
            "semantic_similarity": semantic_similarity,
            "similarity": hybrid_score  # For backward compatibility
        })

    # 5️⃣ Sort by hybrid score and return top N
    formatted_results.sort(key=lambda x: x["similarity"], reverse=True)

    return formatted_results[:top_n]


#Collaborative Filtering Recommendation can be added here similarly
async def get_collaborative_filtering_recommendations(candidate_id, top_n=5):
    # Placeholder for collaborative filtering logic
    # This would typically involve querying a trained CF model
    # and returning recommendations based on candidate interactions
    pass


#Hybrid Recommendation can be added here similarly









if __name__ == "__main__":
    import json

    print("🚀 Starting Content-Based Recommendation Test (with Skill Overlap Weighting)...")
    print("=" * 80)

    query_item = {
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        "title": "Back-end developer",
        "description": "We are looking for a skilled Back-end developer with experience in "
                       "Python and FastAPI to join our dynamic team. The ideal"
                       " candidate will have a strong background in building "
                       "scalable web applications and working with cloud services like AWS. "
                       "Familiarity with PostgreSQL and containerization using Docker is a must."
    }

    print("\n📋 Query Item:")
    print(json.dumps(query_item, indent=2, ensure_ascii=False))
    print("\n" + "=" * 80)

    try:
        print("\n🔍 Searching for similar jobs (Hybrid: Semantic + Skill Overlap)...")
        recs = asyncio.run(get_content_based_recommendations(query_item, top_n=5, skill_weight=0.4))

        if not recs:
            print("\n❌ No recommendations found. The JobPosting collection might be empty.")
        else:
            print(f"\n✅ Found {len(recs)} recommendations:\n")
            for idx, r in enumerate(recs, 1):
                print(f"\n{'='*80}")
                print(f"#{idx} - {r['title']}")
                print(f"{'='*80}")
                print(f"🆔 Job ID: {r['job_id']}")
                print(f"🧠 Skills: {r['skills']}")
                print(f"📊 Scores:")
                print(f"   • Semantic Similarity: {r['semantic_similarity']:.3f}")
                print(f"   • Similarity: {r['similarity']:.3f} (Overall)")
                print(f"📝 Description: {r['description'][:150]}...")

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Close the Weaviate connection properly
        print("\n" + "=" * 80)
        print("🧹 Closing connections...")
        manager.close()
        print("✅ Done!")

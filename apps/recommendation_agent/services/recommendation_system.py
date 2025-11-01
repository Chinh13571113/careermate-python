import asyncio

import joblib
import numpy as np
import pandas as pd
import os
import django
import sys
from sqlalchemy import create_engine
from asgiref.sync import sync_to_async

from dotenv import load_dotenv
from google import genai
from surprise import Reader, Dataset, SVD, accuracy
from surprise.model_selection import train_test_split

from apps.recommendation_agent.services.weaviate_service import query_weaviate_async, manager
from apps.recommendation_agent.services.overlap_skill import calculate_skill_overlap

load_dotenv()
MODEL_PATH = "cf_model.pkl"

# Setup Django environment FIRST before importing models
django_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(django_base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

# NOW import Django models after setup
from django.conf import settings
from apps.recommendation_agent.models import Candidate, JobPostings

# Create SQLAlchemy engine from Django database settings
def get_sqlalchemy_engine():
    """Create SQLAlchemy engine from Django database settings"""
    db_settings = settings.DATABASES['default']
    engine = db_settings.get('ENGINE', '')

    if 'postgresql' in engine:
        db_url = f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 5432)}/{db_settings['NAME']}"
    elif 'mysql' in engine:
        db_url = f"mysql+pymysql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 3306)}/{db_settings['NAME']}"
    else:
        # SQLite or other
        db_url = f"sqlite:///{db_settings['NAME']}"

    return create_engine(db_url)

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
        combined_parts.extend([skills_text] * int(weights.get("skills", 0.5) * 10))  # High weight for skills
    if title_text:
        combined_parts.extend([title_text] * int(weights.get("title", 0.3) * 10))  # Medium weight for title
    if description_text:
        combined_parts.extend([description_text] * int(weights.get("description", 0.15) * 10))

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
def _collaborative_filtering_sync(candidate_id, job_ids, n=5):
    """Dự đoán top job cho candidate dựa vào model CF (SVD) với thông tin chi tiết"""
    if not os.path.exists(MODEL_PATH):
        print("⚠️ CF model not found, returning empty results.")
        return []

    model = joblib.load(MODEL_PATH)

    # Predict scores for all jobs
    predictions = [(job_id, model.predict(candidate_id, job_id).est) for job_id in job_ids]
    predictions = sorted(predictions, key=lambda x: x[1], reverse=True)[:n]

    # Get detailed job information from database
    predicted_job_ids = [job_id for job_id, _ in predictions]
    jobs = JobPostings.objects.filter(id__in=predicted_job_ids).values(
        'id', 'title', 'description', 'address'
    )

    # Create a mapping of job_id to job details
    job_details_map = {job['id']: job for job in jobs}

    # Combine predictions with job details
    detailed_results = []
    for job_id, score in predictions:
        job_info = job_details_map.get(job_id, {})

        # Get skills from Weaviate or CSV (if available)
        skills = "N/A"
        try:
            # Try to get from data_jp CSV
            job_row = data_jp[data_jp['id'] == job_id]
            if not job_row.empty:
                skills = job_row.iloc[0].get('skills', 'N/A')
        except Exception:
            pass

        detailed_results.append({
            "job_id": job_id,
            "title": job_info.get('title', 'Unknown'),
            "description": job_info.get('description', ''),
            "address": job_info.get('address', ''),
            "skills": skills,
            "cf_score": round(score, 4)
        })

    return detailed_results

async def get_collaborative_filtering_recommendations(candidate_id, job_ids, model, n=5):
    """Async wrapper for collaborative filtering"""
    return await sync_to_async(_collaborative_filtering_sync)(candidate_id, job_ids, n)


#Hybrid Recommendation can be added here similarly

async def get_hybrid_job_recommendations(candidate_id: int, query_item: dict, job_ids: list, top_n: int = 5):
    # 1️⃣ Get Content-Based recommendations (semantic + skill overlap)
    content_results = await get_content_based_recommendations(query_item, top_n=top_n * 2)
    content_scores = {r["job_id"]: r["similarity"] for r in content_results}

    # 2️⃣ Try Collaborative Filtering (fallback to None if data too small)
    try:
        cf_results = await get_collaborative_filtering_recommendations(candidate_id, job_ids, model=None, n=top_n * 2)
        # CF results now return detailed dictionaries with job info
        cf_scores = {job["job_id"]: job["cf_score"] for job in cf_results}
        has_cf_data = True
    except Exception as e:
        print(f"[⚠️ CF skipped: {e}]")
        cf_results = []  # Initialize to empty list when exception occurs
        cf_scores = {}
        has_cf_data = False

    # 3️⃣ Set dynamic weights
    # New system → content weight high, CF low
    if not has_cf_data:
        content_weight = 1.0
        cf_weight = 0.0
    else:
        content_weight = 0.8  # tune dynamically when more feedback grows
        cf_weight = 0.2

    # 4️⃣ Combine both scores
    hybrid_combined = {}
    for job_id, c_score in content_scores.items():
        cf_score = cf_scores.get(job_id, 0)
        hybrid_score = (content_weight * c_score) + (cf_weight * cf_score)
        hybrid_combined[job_id] = round(hybrid_score, 4)

    # 5️⃣ Merge metadata from content results
    hybrid_ranked = sorted(content_results, key=lambda x: hybrid_combined.get(x["job_id"], 0), reverse=True)[:top_n]

    # 6️⃣ Attach hybrid score to results
    for r in hybrid_ranked:
        r["final_score"] = hybrid_combined.get(r["job_id"], r["similarity"])
        r["source_weight"] = {"content": content_weight, "cf": cf_weight}

    return  {
        "content_based": content_results[:top_n],
        "collaborative": cf_results[:top_n],  # Now returns detailed job info
        "hybrid_top": hybrid_ranked
    }


def _query_all_jobs_sync():
    """
    Synchronous function to get ACTIVE jobs from PostgreSQL (ORM)
    """
    jobs = JobPostings.objects.filter(status="ACTIVE").values(
        "id", "title", "description", "address"
    )

    # Chuẩn hóa về định dạng mà hybrid model dùng
    job_list = [{"job_id": job["id"], "title": job["title"],
                 "description": job["description"], "address": job["address"]}
                for job in jobs]
    return job_list

def query_all_jobs():
    """
    Lấy danh sách job đang ACTIVE từ PostgreSQL (ORM)
    Wrapper for sync context (still synchronous for backward compatibility)
    """
    return _query_all_jobs_sync()

async def query_all_jobs_async():
    """
    Async wrapper for query_all_jobs
    """
    return await sync_to_async(_query_all_jobs_sync)()


# if __name__ == "__main__":
#     import json
#
#     print("🚀 Starting Content-Based Recommendation Test (with Skill Overlap Weighting)...")
#     print("=" * 80)
#
#     query_item = {
#         "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
#         "title": "Back-end developer",
#         "description": "We are looking for a skilled Back-end developer with experience in "
#                        "Python and FastAPI to join our dynamic team. The ideal"
#                        " candidate will have a strong background in building "
#                        "scalable web applications and working with cloud services like AWS. "
#                        "Familiarity with PostgreSQL and containerization using Docker is a must."
#     }
#
#     print("\n📋 Query Item:")
#     print(json.dumps(query_item, indent=2, ensure_ascii=False))
#     print("\n" + "=" * 80)
#
#     try:
#         print("\n🔍 Searching for similar jobs (Hybrid: Semantic + Skill Overlap)...")
#         recs = asyncio.run(get_content_based_recommendations(query_item, top_n=5, skill_weight=0.4))
#
#         if not recs:
#             print("\n❌ No recommendations found. The JobPosting collection might be empty.")
#         else:
#             print(f"\n✅ Found {len(recs)} recommendations:\n")
#             for idx, r in enumerate(recs, 1):
#                 print(f"\n{'='*80}")
#                 print(f"#{idx} - {r['title']}")
#                 print(f"{'='*80}")
#                 print(f"🆔 Job ID: {r['job_id']}")
#                 print(f"🧠 Skills: {r['skills']}")
#                 print(f"📊 Scores:")
#                 print(f"   • Semantic Similarity: {r['semantic_similarity']:.3f}")
#                 print(f"   • Similarity: {r['similarity']:.3f} (Overall)")
#                 print(f"📝 Description: {r['description'][:150]}...")
#
#     except Exception as e:
#         print(f"\n❌ Error occurred: {str(e)}")
#         import traceback
#         traceback.print_exc()
#
#     finally:
#         # Close the Weaviate connection properly
#         print("\n" + "=" * 80)
#         print("🧹 Closing connections...")
#         manager.close()
#         print("✅ Done!")

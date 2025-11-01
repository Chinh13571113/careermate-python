"""
Test script for Collaborative Filtering Recommendations
Kiểm tra dữ liệu trả về từ collaborative filtering model
"""
import os
import django
import sys
import asyncio
import pandas as pd
from sqlalchemy import create_engine

# Setup Django environment
django_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(django_base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from django.conf import settings
from apps.recommendation_agent.services.recommendation_system import (
    get_collaborative_filtering_recommendations,
    get_hybrid_job_recommendations,
    query_all_jobs_async
)


def get_sqlalchemy_engine():
    """Create SQLAlchemy engine from Django database settings"""
    db_settings = settings.DATABASES['default']
    engine = db_settings.get('ENGINE', '')

    if 'postgresql' in engine:
        db_url = f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 5432)}/{db_settings['NAME']}"
    elif 'mysql' in engine:
        db_url = f"mysql+pymysql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings.get('PORT', 3306)}/{db_settings['NAME']}"
    else:
        db_url = f"sqlite:///{db_settings['NAME']}"

    return create_engine(db_url)


def check_feedback_data():
    """Kiểm tra dữ liệu feedback trong database"""
    print("=" * 80)
    print("📊 KIỂM TRA DỮ LIỆU FEEDBACK")
    print("=" * 80)

    engine = get_sqlalchemy_engine()
    try:
        # Lấy tất cả feedback data
        query = "SELECT candidate_id, job_id, score FROM job_feedback"
        df = pd.read_sql(query, engine)

        if df.empty:
            print("\n❌ Không có dữ liệu feedback trong database!")
            print("💡 Hãy thêm dữ liệu feedback trước khi test collaborative filtering.")
            return False

        print(f"\n✅ Tổng số feedback records: {len(df)}")
        print(f"📈 Số candidates có feedback: {df['candidate_id'].nunique()}")
        print(f"📈 Số jobs có feedback: {df['job_id'].nunique()}")
        print(f"📊 Score trung bình: {df['score'].mean():.3f}")
        print(f"📊 Score min/max: {df['score'].min():.3f} / {df['score'].max():.3f}")

        # Hiển thị 10 records đầu tiên
        print("\n📋 Sample feedback data (10 records đầu tiên):")
        print(df.head(10).to_string(index=False))

        # Thống kê theo candidate
        print("\n👥 Top 5 candidates có nhiều feedback nhất:")
        candidate_counts = df['candidate_id'].value_counts().head(5)
        for candidate_id, count in candidate_counts.items():
            avg_score = df[df['candidate_id'] == candidate_id]['score'].mean()
            print(f"   Candidate {candidate_id}: {count} feedbacks (avg score: {avg_score:.3f})")

        return True
    finally:
        engine.dispose()


async def test_collaborative_filtering(candidate_id=None, top_n=5):
    """Test collaborative filtering recommendations"""
    print("\n" + "=" * 80)
    print("🧪 TEST COLLABORATIVE FILTERING")
    print("=" * 80)

    # Nếu không có candidate_id, lấy candidate đầu tiên có feedback
    if candidate_id is None:
        engine = get_sqlalchemy_engine()
        try:
            query = "SELECT DISTINCT candidate_id FROM job_feedback LIMIT 1"
            df = pd.read_sql(query, engine)
            if df.empty:
                print("\n❌ Không có candidate nào có feedback!")
                return
            candidate_id = df['candidate_id'].iloc[0]
        finally:
            engine.dispose()

    print(f"\n🔍 Testing với Candidate ID: {candidate_id}")
    print(f"📊 Số recommendations yêu cầu: {top_n}")

    # Lấy danh sách job IDs
    job_ids = [j["job_id"] for j in await query_all_jobs_async()]
    print(f"📋 Tổng số jobs trong hệ thống: {len(job_ids)}")

    try:
        print("\n⏳ Đang chạy collaborative filtering...")
        cf_results = await get_collaborative_filtering_recommendations(
            candidate_id=candidate_id,
            job_ids=job_ids,
            model=None,
            n=top_n
        )

        print(f"\n✅ Collaborative Filtering hoàn tất!")
        print(f"📊 Số recommendations trả về: {len(cf_results)}")

        print("\n" + "=" * 80)
        print("📋 KẾT QUẢ COLLABORATIVE FILTERING:")
        print("=" * 80)

        for idx, job in enumerate(cf_results, 1):
            print(f"\n#{idx} - {job['title']}")
            print(f"   Job ID: {job['job_id']}")
            print(f"   ⭐ CF Score: {job['cf_score']:.4f}")
            print(f"   📍 Address: {job.get('address', 'N/A')}")
            print(f"   🛠️  Skills: {job.get('skills', 'N/A')}")
            print(f"   💼 Title: {job.get('title', 'N/A')}")
            if job.get('description'):
                print(f"   📝 Description: {job['description'][:150]}...")

        return cf_results

    except Exception as e:
        print(f"\n❌ Lỗi khi chạy collaborative filtering: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_hybrid_recommendations(candidate_id=None, top_n=5):
    """Test hybrid recommendations (Content-Based + Collaborative Filtering)"""
    print("\n" + "=" * 80)
    print("🧪 TEST HYBRID RECOMMENDATIONS")
    print("=" * 80)

    # Nếu không có candidate_id, lấy candidate đầu tiên có feedback
    if candidate_id is None:
        engine = get_sqlalchemy_engine()
        try:
            query = "SELECT DISTINCT candidate_id FROM job_feedback LIMIT 1"
            df = pd.read_sql(query, engine)
            if df.empty:
                print("\n❌ Không có candidate nào có feedback!")
                return
            candidate_id = df['candidate_id'].iloc[0]
        finally:
            engine.dispose()

    print(f"\n🔍 Testing với Candidate ID: {candidate_id}")

    # Sample query item
    query_item = {
        "skills": ["Python", "Django", "PostgreSQL", "REST API"],
        "title": "Backend Developer",
        "description": "Experienced backend developer with strong Python skills"
    }

    print(f"\n📋 Query Item:")
    print(f"   Skills: {', '.join(query_item['skills'])}")
    print(f"   Title: {query_item['title']}")

    # Lấy danh sách job IDs
    job_ids = [j["job_id"] for j in await query_all_jobs_async()]

    try:
        print("\n⏳ Đang chạy hybrid recommendations...")
        hybrid_results = await get_hybrid_job_recommendations(
            candidate_id=candidate_id,
            query_item=query_item,
            job_ids=job_ids,
            top_n=top_n
        )

        print(f"\n✅ Hybrid Recommendations hoàn tất!")

        # Content-Based Results
        print("\n" + "=" * 80)
        print("📋 CONTENT-BASED RECOMMENDATIONS:")
        print("=" * 80)
        for idx, job in enumerate(hybrid_results['content_based'], 1):
            print(f"\n#{idx} - {job['title']}")
            print(f"   Job ID: {job['job_id']}")
            print(f"   ⭐ Similarity Score: {job['similarity']:.4f}")
            print(f"   🎯 Semantic Similarity: {job['semantic_similarity']:.4f}")
            print(f"   Skills: {job['skills'][:100]}...")

        # Collaborative Filtering Results
        print("\n" + "=" * 80)
        print("📋 COLLABORATIVE FILTERING RECOMMENDATIONS:")
        print("=" * 80)
        if hybrid_results['collaborative']:
            for idx, cf_job in enumerate(hybrid_results['collaborative'], 1):
                print(f"\n#{idx} - {cf_job['title']}")
                print(f"   Job ID: {cf_job['job_id']}")
                print(f"   ⭐ CF Score: {cf_job['cf_score']:.4f}")
                print(f"   📍 Address: {cf_job.get('address', 'N/A')}")
                print(f"   🛠️  Skills: {cf_job.get('skills', 'N/A')[:80]}...")
        else:
            print("\n⚠️ Không có CF recommendations (có thể do thiếu dữ liệu)")

        # Hybrid Results
        print("\n" + "=" * 80)
        print("📋 HYBRID RECOMMENDATIONS (FINAL):")
        print("=" * 80)
        for idx, job in enumerate(hybrid_results['hybrid_top'], 1):
            print(f"\n#{idx} - {job['title']}")
            print(f"   Job ID: {job['job_id']}")
            print(f"   ⭐ Final Score: {job['final_score']:.4f}")
            print(f"   📊 Weights: Content={job['source_weight']['content']:.2f}, CF={job['source_weight']['cf']:.2f}")
            print(f"   Skills: {job['skills'][:100]}...")

        return hybrid_results

    except Exception as e:
        print(f"\n❌ Lỗi khi chạy hybrid recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main test function"""
    print("🚀 COLLABORATIVE FILTERING TEST SUITE")
    print("=" * 80)

    # 1. Kiểm tra dữ liệu feedback
    has_data = check_feedback_data()

    if not has_data:
        print("\n💡 Hướng dẫn thêm dữ liệu feedback:")
        print("   1. Sử dụng API để candidates tương tác với jobs")
        print("   2. Hoặc chạy script seed_feedback_data.py để tạo dữ liệu mẫu")
        return

    # 2. Test Collaborative Filtering
    cf_results = await test_collaborative_filtering(candidate_id=None, top_n=5)

    # 3. Test Hybrid Recommendations
    if cf_results:
        await test_hybrid_recommendations(candidate_id=None, top_n=5)

    print("\n" + "=" * 80)
    print("✅ TEST HOÀN TẤT!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

"""
Script để thêm dữ liệu feedback mẫu cho collaborative filtering
"""
import os
import django
import sys
import random

# Setup Django environment
django_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(django_base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from django.db import connection

def seed_feedback_data():
    """Thêm dữ liệu feedback mẫu"""
    print("🚀 SEED FEEDBACK DATA")
    print("=" * 80)

    # Lấy danh sách candidates và jobs
    with connection.cursor() as cursor:
        # Get existing candidates
        cursor.execute("SELECT candidate_id FROM candidate LIMIT 10")
        candidates = [row[0] for row in cursor.fetchall()]

        # Get existing jobs
        cursor.execute("SELECT id FROM job_posting WHERE status = 'ACTIVE' LIMIT 20")
        jobs = [row[0] for row in cursor.fetchall()]

        if not candidates or not jobs:
            print("❌ Không tìm thấy candidates hoặc jobs trong database!")
            print("💡 Hãy đảm bảo có dữ liệu candidates và jobs trước.")
            return

        print(f"✅ Tìm thấy {len(candidates)} candidates và {len(jobs)} jobs")

        # Xóa feedback data cũ
        cursor.execute("DELETE FROM job_feedback")
        print("🗑️  Đã xóa dữ liệu feedback cũ")

        # Tạo feedback data mới
        feedback_count = 0
        for candidate_id in candidates:
            # Mỗi candidate tương tác với 3-7 jobs ngẫu nhiên
            num_interactions = random.randint(3, min(7, len(jobs)))
            selected_jobs = random.sample(jobs, num_interactions)

            for job_id in selected_jobs:
                # Score ngẫu nhiên từ 0.3 đến 1.0 (bias về positive)
                score = round(random.uniform(0.3, 1.0), 2)

                # Feedback type chỉ có 2 loại hợp lệ: 'apply' và 'like'
                feedback_type = random.choice(['apply', 'like'])

                cursor.execute(
                    "INSERT INTO job_feedback (candidate_id, job_id, feedback_type, score) VALUES (%s, %s, %s, %s)",
                    [candidate_id, job_id, feedback_type, score]
                )
                feedback_count += 1

        print(f"✅ Đã tạo {feedback_count} feedback records")

        # Hiển thị thống kê
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT candidate_id) as unique_candidates,
                COUNT(DISTINCT job_id) as unique_jobs,
                AVG(score) as avg_score,
                MIN(score) as min_score,
                MAX(score) as max_score
            FROM job_feedback
        """)
        stats = cursor.fetchone()

        print("\n📊 THỐNG KÊ FEEDBACK DATA:")
        print(f"   Tổng records: {stats[0]}")
        print(f"   Unique candidates: {stats[1]}")
        print(f"   Unique jobs: {stats[2]}")
        print(f"   Score trung bình: {stats[3]:.3f}")
        print(f"   Score min/max: {stats[4]:.3f} / {stats[5]:.3f}")

        print("\n✅ Seed data hoàn tất!")

if __name__ == "__main__":
    seed_feedback_data()

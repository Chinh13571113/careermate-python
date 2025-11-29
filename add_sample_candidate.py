"""
Script to add a sample candidate with feedback data for CF training
This is for development/testing purposes only
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from apps.recommendation_agent.models import Account, Candidate, JobPostings, JobFeedback

def add_sample_data():
    print("=" * 60)
    print("Adding Sample Candidate for CF Training")
    print("=" * 60)

    try:
        # Create a sample account
        account, created = Account.objects.get_or_create(
            email='sample.candidate@example.com',
            defaults={
                'full_name': 'Sample Candidate',
                'password': 'hashed_password_here',
                'status': 'ACTIVE'
            }
        )

        if created:
            print(f"\n✓ Created sample account: {account.email}")
        else:
            print(f"\n✓ Sample account already exists: {account.email}")

        # Create a sample candidate
        candidate, created = Candidate.objects.get_or_create(
            account=account,
            defaults={
                'fullname': 'Sample Candidate',
                'title': 'Software Developer',
                'job_level': 'Junior',
                'exp_year': 2,
            }
        )

        if created:
            print(f"✓ Created sample candidate: {candidate.fullname} (ID: {candidate.candidate_id})")
        else:
            print(f"✓ Sample candidate already exists: {candidate.fullname} (ID: {candidate.candidate_id})")

        # Get available jobs
        jobs = list(JobPostings.objects.all()[:3])
        print(f"\n✓ Found {len(jobs)} jobs to create interactions")

        # Create sample feedback
        feedback_created = 0
        for i, job in enumerate(jobs):
            feedback_type = ['like', 'save', 'apply'][i % 3]

            feedback, created = JobFeedback.objects.get_or_create(
                candidate=candidate,
                job=job,
                feedback_type=feedback_type,
                defaults={'score': 1.0 if feedback_type != 'dislike' else -1.0}
            )

            if created:
                feedback_created += 1
                print(f"  - {candidate.fullname} -> {job.title}: {feedback_type}")

        print(f"\n✓ Created {feedback_created} new feedback records")

        # Check totals
        total_candidates = Candidate.objects.count()
        total_feedback = JobFeedback.objects.exclude(feedback_type='dislike').count()

        print(f"\nDatabase Status:")
        print(f"  Total Candidates: {total_candidates}")
        print(f"  Total Feedback: {total_feedback}")

        if total_candidates >= 2:
            print(f"\n✓ You now have enough data to train the CF model!")
            print(f"  Run: python train_cf_model.py")

        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_sample_data()


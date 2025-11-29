"""
Seed script to create sample feedback data for CF model training
This creates synthetic user interactions to train the collaborative filtering model
"""
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from apps.recommendation_agent.models import JobFeedback, Candidate, JobPostings

def seed_feedback_data():
    print("=" * 60)
    print("Seeding Feedback Data for CF Model Training")
    print("=" * 60)

    # Get all candidates and jobs
    candidates = list(Candidate.objects.all())
    jobs = list(JobPostings.objects.filter(status='APPROVED'))

    print(f"\nFound {len(candidates)} candidates and {len(jobs)} jobs")

    if len(candidates) < 2 or len(jobs) < 2:
        print("\n⚠ Warning: Need at least 2 candidates and 2 jobs for meaningful CF training")
        print("Current data is insufficient for collaborative filtering.")
        print("\nFor now, I'll create minimal data to make the system work.")
        return False

    # Clear existing feedback (optional)
    existing_count = JobFeedback.objects.count()
    print(f"\nExisting feedback records: {existing_count}")

    # Generate synthetic feedback
    feedback_types = ['like', 'save', 'apply', 'dislike']
    feedback_weights = [0.4, 0.3, 0.2, 0.1]  # Probability distribution

    created_count = 0

    for candidate in candidates:
        # Each candidate interacts with 50-80% of jobs
        num_interactions = random.randint(len(jobs) // 2, int(len(jobs) * 0.8))
        selected_jobs = random.sample(jobs, min(num_interactions, len(jobs)))

        for job in selected_jobs:
            # Random feedback type
            feedback_type = random.choices(feedback_types, weights=feedback_weights)[0]

            # Create feedback if it doesn't exist
            feedback, created = JobFeedback.objects.get_or_create(
                candidate=candidate,
                job=job,
                feedback_type=feedback_type,
                defaults={
                    'score': 1.0 if feedback_type != 'dislike' else -1.0,
                }
            )

            if created:
                created_count += 1

    print(f"\n✓ Created {created_count} new feedback records")
    print(f"✓ Total feedback records: {JobFeedback.objects.count()}")

    # Show breakdown
    print(f"\nFeedback breakdown:")
    for ftype in feedback_types:
        count = JobFeedback.objects.filter(feedback_type=ftype).count()
        print(f"  - {ftype}: {count}")

    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = seed_feedback_data()
        if not success:
            print("\n⚠ Insufficient data to train CF model properly.")
            print("The system will work but recommendations will be limited.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


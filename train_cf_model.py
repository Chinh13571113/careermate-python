"""
Script to train the Collaborative Filtering model
Run this script to initialize the CF model with existing feedback data
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from apps.recommendation_agent.services.collaborative_filtering import cf_service
from apps.recommendation_agent.models import JobFeedback, Candidate, JobPostings

def main():
    print("=" * 60)
    print("Training Collaborative Filtering Model")
    print("=" * 60)

    try:
        # Check current data availability
        print(f"\nChecking data availability...")
        candidates = Candidate.objects.count()
        jobs = JobPostings.objects.count()
        feedbacks = JobFeedback.objects.exclude(feedback_type='dislike').count()

        print(f"  Candidates: {candidates}")
        print(f"  Job Postings: {jobs}")
        print(f"  Feedback records (excluding dislikes): {feedbacks}")

        # Check if data is sufficient
        if candidates < 2:
            print(f"\n❌ Insufficient data for training!")
            print(f"\n⚠ Collaborative Filtering requires at least 2 users (candidates).")
            print(f"   Current: {candidates} candidate(s)")
            print(f"\nWhat you need to do:")
            print(f"  1. Create at least 1 more candidate in your database")
            print(f"  2. Add job interactions (likes, saves, applies) for both candidates")
            print(f"  3. Then run this script again to train the model")
            print(f"\nFor now, the system will work with content-based recommendations only.")
            print("=" * 60)
            return False

        if jobs < 2:
            print(f"\n❌ Insufficient job data!")
            print(f"   Current: {jobs} job(s)")
            print(f"   Required: At least 2 jobs")
            return False

        if feedbacks < 4:
            print(f"\n⚠ Warning: Very limited feedback data ({feedbacks} records)")
            print(f"   Recommendations may not be accurate.")

        # Check current model status
        stats = cf_service.get_model_stats()
        print(f"\nCurrent Model Status:")
        print(f"  Model exists: {stats.get('model_exists', False)}")

        if stats.get('error'):
            print(f"  Status: {stats['error']}")

        # Train the model
        print(f"\nStarting training...")
        print(f"  Embedding size: 64")
        print(f"  Learning rate: 0.001")
        print(f"  Epochs: 10")
        print(f"  Model type: BPR")

        training_stats = cf_service.train_model(
            embedding_size=64,
            learning_rate=0.001,
            epochs=10,
            model_type='BPR'
        )

        print(f"\n✓ Training completed successfully!")
        print(f"\nTraining Statistics:")
        print(f"  Users: {training_stats.get('num_users', 'N/A')}")
        print(f"  Jobs: {training_stats.get('num_jobs', 'N/A')}")
        print(f"  Interactions: {training_stats.get('num_interactions', 'N/A')}")
        print(f"  Embedding dimension: {training_stats.get('embedding_size', 'N/A')}")

        if 'test_results' in training_stats:
            print(f"\n  Test Results:")
            for metric, value in training_stats['test_results'].items():
                print(f"    - {metric}: {value:.4f}")

        print(f"\nModel saved to: {training_stats.get('model_path', 'N/A')}")
        print("=" * 60)
        return True

    except ValueError as e:
        print(f"\n❌ Training failed: {e}")
        print("\n" + "=" * 60)
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False

if __name__ == "__main__":
    main()

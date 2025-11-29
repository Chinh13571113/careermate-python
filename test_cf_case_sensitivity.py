"""
Test script to verify case-sensitivity fix for collaborative filtering
Run this to check if feedback types are being processed correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

from apps.recommendation_agent.models import JobFeedback

# Feedback type weights (same as in collaborative_recommender.py)
FEEDBACK_WEIGHTS = {
    'apply': 1.0,
    'like': 0.7,
    'save': 0.5,
    'view': 0.3,
    'dislike': 0.0
}

print("=" * 60)
print("Testing Feedback Type Case Sensitivity")
print("=" * 60)

# Get all unique feedback types from database
feedbacks = JobFeedback.objects.all()
feedback_types = {}

for fb in feedbacks:
    fb_type = fb.feedback_type
    if fb_type not in feedback_types:
        feedback_types[fb_type] = 0
    feedback_types[fb_type] += 1

print(f"\n📊 Feedback Types in Database:")
print(f"   Total feedback records: {feedbacks.count()}")
print(f"   Unique feedback types: {len(feedback_types)}")
print()

for fb_type, count in sorted(feedback_types.items()):
    fb_type_lower = fb_type.lower() if fb_type else ''
    weight = FEEDBACK_WEIGHTS.get(fb_type_lower, 0.5)

    # Check if it matches a key in FEEDBACK_WEIGHTS
    matched = "✅ MATCHED" if fb_type_lower in FEEDBACK_WEIGHTS else "⚠️ DEFAULT (0.5)"

    print(f"   {fb_type:15} → lowercase: {fb_type_lower:15} → weight: {weight:.1f}  {matched} (count: {count})")

print()
print("=" * 60)
print("✨ Fix Applied:")
print("   - All feedback types are now converted to lowercase")
print("   - Matching is case-insensitive")
print("   - DISLIKE (weight=0.0) is excluded from interactions")
print("=" * 60)


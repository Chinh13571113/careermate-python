# apps/recommendations/tasks.py
from celery import shared_task
from apps.recommendation_agent.services.train_cf_model import train_cf_model

@shared_task
def train_cf_model_task():
    """Celery task retrain collaborative filtering model"""
    print("🧠 Starting CF model retraining...")
    model = train_cf_model()
    if model:
        print("✅ CF model retrained successfully!")
    else:
        print("⚠️ CF model not updated (insufficient data).")






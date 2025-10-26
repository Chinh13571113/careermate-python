import os
import warnings
from celery import Celery
from celery.schedules import crontab

# Suppress Triton warnings about missing CUDA binaries
warnings.filterwarnings('ignore', message='Failed to find.*', module='triton.knobs')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Careermate.settings")

app = Celery("Careermate")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Periodic tasks configuration
app.conf.beat_schedule = {
    'sync-jobs-every-5-minutes': {
        'task': 'apps.recommendation_agent.tasks.periodic_sync_jobs',
        'schedule': 300.0,  # Every 5 minutes (300 seconds)
    },
    'full-resync-daily': {
        'task': 'apps.recommendation_agent.tasks.full_resync',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2:00 AM
    },
}

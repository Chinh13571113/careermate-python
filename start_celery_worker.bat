@echo off
echo Starting Celery Worker with Auto-Reload...
echo.
echo This worker will automatically restart after each task to pick up code changes.
echo Worker recycling is enabled via celery_app.py configuration.
echo.

REM Set environment variable for development mode
set DEBUG=True

REM Start Celery worker with solo pool (required for Windows)
REM Worker will restart after each task due to worker_max_tasks_per_child=1 in celery_app.py
celery -A Careermate worker --loglevel=info --pool=solo

pause

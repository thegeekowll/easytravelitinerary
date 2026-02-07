"""
Celery application configuration.

This module configures Celery for async task processing including:
- Email sending
- PDF generation
- Notification scheduling
- Analytics processing
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "travel_agency",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=["json"],
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "check-3-day-arrival-notifications": {
        "task": "app.services.celery_tasks.check_upcoming_arrivals",
        "schedule": crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
    "cleanup-old-notifications": {
        "task": "app.services.celery_tasks.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    "cleanup-old-email-logs": {
        "task": "app.services.celery_tasks.cleanup_old_email_logs",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Run weekly on Sunday at 3 AM
    },
}

# Auto-discover tasks from all installed apps
celery_app.autodiscover_tasks(["app.services"])

# Task routes (optional - for task-specific queues)
celery_app.conf.task_routes = {
    "app.services.celery_tasks.send_email_async": {"queue": "emails"},
    "app.services.celery_tasks.generate_pdf_async": {"queue": "pdfs"},
    "app.services.celery_tasks.check_upcoming_arrivals": {"queue": "notifications"},
}


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery is working."""
    print(f"Request: {self.request!r}")
    return "Celery is working!"

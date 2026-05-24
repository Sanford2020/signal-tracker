from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "signal_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "source-checks-run-due": {
            "task": "workers.tasks.run_due_source_checks",
            "schedule": settings.source_check_interval_seconds,
            "kwargs": {"limit": 50},
        },
        "lifecycle-dormancy-run": {
            "task": "workers.tasks.run_lifecycle_dormancy",
            "schedule": settings.lifecycle_worker_interval_seconds,
            "kwargs": {"limit": 100, "reason": "scheduled lifecycle worker"},
        },
        "notification-delivery-run": {
            "task": "workers.tasks.deliver_pending_notifications",
            "schedule": settings.notification_delivery_interval_seconds,
            "kwargs": {"limit": 100},
        },
    },
)

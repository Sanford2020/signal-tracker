from app.db.session import SessionLocal
from app.modules.lifecycle.worker import run_lifecycle_worker
from app.modules.notifications.service import run_notification_delivery
from app.modules.source_checks.providers import ProviderBackedSourceChecker, get_default_provider_registry
from app.modules.source_checks.service import run_source_checks
from app.schemas.lifecycle_worker import LifecycleWorkerRunRequest
from app.schemas.notifications import NotificationDeliveryRunRequest
from app.schemas.source_checks import SourceCheckRunRequest
from workers.celery_app import celery_app


@celery_app.task(name="workers.tasks.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="workers.tasks.run_due_source_checks")
def run_due_source_checks(limit: int = 50) -> dict:
    db = SessionLocal()
    try:
        data = run_source_checks(
            db,
            SourceCheckRunRequest(limit=limit),
            checker=ProviderBackedSourceChecker(get_default_provider_registry()),
        )
        return {
            "run_id": str(data.run.id),
            "status": data.run.status,
            "checked_query_count": data.run.checked_query_count,
            "result_count": data.run.result_count,
        }
    finally:
        db.close()


@celery_app.task(name="workers.tasks.run_lifecycle_dormancy")
def run_lifecycle_dormancy(limit: int = 100, reason: str = "scheduled lifecycle worker") -> dict:
    db = SessionLocal()
    try:
        data = run_lifecycle_worker(db, LifecycleWorkerRunRequest(limit=limit, reason=reason))
        return {
            "checked_count": data.checked_count,
            "transitioned_count": data.transitioned_count,
            "items": [
                {
                    "intel_file_id": str(item.intel_file_id),
                    "previous_status": item.previous_status.value,
                    "next_status": item.next_status.value,
                    "reason": item.reason,
                }
                for item in data.items
            ],
        }
    finally:
        db.close()


@celery_app.task(name="workers.tasks.deliver_pending_notifications")
def deliver_pending_notifications(limit: int = 100) -> dict:
    db = SessionLocal()
    try:
        data = run_notification_delivery(
            db,
            NotificationDeliveryRunRequest(limit=limit),
            workspace_id=None,
        )
        return {
            "checked_alert_count": data.checked_alert_count,
            "delivered_count": data.delivered_count,
            "skipped_count": data.skipped_count,
        }
    finally:
        db.close()

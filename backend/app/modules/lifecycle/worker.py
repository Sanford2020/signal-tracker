from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import IntelFile
from app.models.enums import LifecycleStatus
from app.modules.lifecycle.service import evaluate_intel_file
from app.schemas.lifecycle import LifecycleEvaluateRequest
from app.schemas.lifecycle_worker import (
    LifecycleWorkerRunData,
    LifecycleWorkerRunRequest,
    LifecycleWorkerTransition,
)

TERMINAL_STATUSES = {
    LifecycleStatus.VERIFIED,
    LifecycleStatus.DEBUNKED,
    LifecycleStatus.NOISE,
}


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def run_lifecycle_worker(db: Session, payload: LifecycleWorkerRunRequest) -> LifecycleWorkerRunData:
    settings = get_settings()
    now = _ensure_utc(payload.now or datetime.now(UTC))
    cutoff = now - timedelta(days=settings.lifecycle_dormancy_days)

    candidates = db.scalars(
        select(IntelFile)
        .where(
            IntelFile.status.not_in(TERMINAL_STATUSES),
            or_(
                IntelFile.last_seen_at <= cutoff,
                IntelFile.status.in_({LifecycleStatus.DORMANT, LifecycleStatus.ARCHIVED}),
            ),
        )
        .order_by(IntelFile.last_seen_at.asc(), IntelFile.id.asc())
        .limit(payload.limit)
    ).all()

    transitions: list[LifecycleWorkerTransition] = []
    for intel_file in candidates:
        result = evaluate_intel_file(
            db,
            intel_file.id,
            LifecycleEvaluateRequest(now=now, reason=payload.reason),
        )
        if result.previous_status != result.next_status:
            transitions.append(
                LifecycleWorkerTransition(
                    intel_file_id=intel_file.id,
                    previous_status=result.previous_status,
                    next_status=result.next_status,
                    reason=result.reason,
                )
            )

    return LifecycleWorkerRunData(
        checked_count=len(candidates),
        transitioned_count=len(transitions),
        items=transitions,
    )

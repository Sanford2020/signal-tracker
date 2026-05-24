from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import UsageEvent
from app.schemas.usage import UsageLimits, UsageSummaryData, UsageTotals

AI_EXTRACTION = "ai_extraction"
SOURCE_CHECK = "source_check"


class UsageLimitError(Exception):
    pass


def month_start(now: datetime | None = None) -> datetime:
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def usage_total(db: Session, workspace_id: UUID | None, usage_type: str) -> int:
    total = db.scalar(
        select(func.coalesce(func.sum(UsageEvent.amount), 0)).where(
            UsageEvent.workspace_id == workspace_id,
            UsageEvent.usage_type == usage_type,
            UsageEvent.created_at >= month_start(),
        )
    )
    return int(total or 0)


def record_usage(
    db: Session,
    *,
    workspace_id: UUID | None,
    usage_type: str,
    amount: int = 1,
    meta: dict | None = None,
) -> UsageEvent:
    event = UsageEvent(
        workspace_id=workspace_id,
        usage_type=usage_type,
        amount=amount,
        meta=meta,
    )
    db.add(event)
    db.flush()
    return event


def assert_usage_available(
    db: Session,
    *,
    workspace_id: UUID | None,
    usage_type: str,
    amount: int = 1,
) -> None:
    settings = get_settings()
    limit = (
        settings.usage_ai_extraction_monthly_limit
        if usage_type == AI_EXTRACTION
        else settings.usage_source_check_monthly_limit
    )
    if usage_total(db, workspace_id, usage_type) + amount > limit:
        raise UsageLimitError(f"Monthly {usage_type} limit exceeded.")


def get_usage_summary(db: Session, *, workspace_id: UUID | None) -> UsageSummaryData:
    settings = get_settings()
    return UsageSummaryData(
        workspace_id=workspace_id,
        month_start=month_start(),
        totals=UsageTotals(
            ai_extraction=usage_total(db, workspace_id, AI_EXTRACTION),
            source_check=usage_total(db, workspace_id, SOURCE_CHECK),
        ),
        limits=UsageLimits(
            ai_extraction=settings.usage_ai_extraction_monthly_limit,
            source_check=settings.usage_source_check_monthly_limit,
        ),
    )

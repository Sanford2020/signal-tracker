from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import Evidence, IntelEvent, IntelFile, RawItem
from app.models.enums import EvidenceType, IntelEventType, LifecycleStatus
from app.schemas.briefings import (
    BriefingEvidence,
    BriefingItem,
    BriefingMeta,
    BriefingScores,
    BriefingSections,
    DailyBriefingData,
    WeeklyBriefingMeta,
    WeeklyBriefingSections,
    WeeklyRetrospectiveData,
)

RISK_THRESHOLD = 7.0


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _scores(file: IntelFile) -> BriefingScores:
    return BriefingScores(
        heat=file.heat_score,
        credibility=file.credibility_score,
        opportunity=file.opportunity_score,
        risk=file.risk_score,
    )


def _key_evidence(file: IntelFile, limit: int = 2) -> list[BriefingEvidence]:
    evidence = sorted(
        file.evidence,
        key=lambda item: item.attached_at or datetime.min.replace(tzinfo=UTC),
        reverse=True,
    )
    items: list[BriefingEvidence] = []
    for link in evidence[:limit]:
        raw_item = link.raw_item
        if raw_item is None:
            continue
        items.append(
            BriefingEvidence(
                raw_item_id=raw_item.id,
                title=raw_item.title,
                url=raw_item.url,
            )
        )
    return items


def _item(file: IntelFile, reason: str) -> BriefingItem:
    return BriefingItem(
        intel_file_id=file.id,
        title=file.title,
        status=file.status,
        reason=reason,
        scores=_scores(file),
        key_evidence=_key_evidence(file),
    )


def _load_files(db: Session, *, workspace_id: UUID | None = None) -> list[IntelFile]:
    stmt = select(IntelFile).options(
        selectinload(IntelFile.evidence)
        .selectinload(Evidence.raw_item)
        .selectinload(RawItem.source),
        selectinload(IntelFile.events),
    )
    if workspace_id is not None:
        stmt = stmt.where(IntelFile.workspace_id == workspace_id)
    return list(db.scalars(stmt).all())


def _recent_events(file: IntelFile, since: datetime) -> list[IntelEvent]:
    return [
        event
        for event in file.events
        if event.event_time is not None and _ensure_utc(event.event_time) >= since
    ]


def _has_recent_event(file: IntelFile, since: datetime, event_type: IntelEventType) -> bool:
    return any(event.event_type == event_type for event in _recent_events(file, since))


def _status_changed_to(file: IntelFile, since: datetime, status: LifecycleStatus) -> bool:
    for event in _recent_events(file, since):
        if event.event_type != IntelEventType.STATUS_CHANGED:
            continue
        metadata = event.metadata_ or {}
        if metadata.get("next_status") == status.value:
            return True
    return False


def _opportunity_crossed(file: IntelFile, since: datetime, threshold: float) -> bool:
    if file.opportunity_score is not None and file.opportunity_score >= threshold:
        return True
    for event in _recent_events(file, since):
        if event.event_type != IntelEventType.SCORE_CHANGED:
            continue
        metadata = event.metadata_ or {}
        score_changes = metadata.get("score_changes") or {}
        previous, current = score_changes.get("opportunity_score", [None, None])
        if previous is not None and current is not None and previous < threshold <= current:
            return True
    return False


def _sort_opportunity(items: list[BriefingItem]) -> list[BriefingItem]:
    return sorted(
        items,
        key=lambda item: (
            item.scores.opportunity if item.scores.opportunity is not None else -1,
            str(item.intel_file_id),
        ),
        reverse=True,
    )


def generate_daily_briefing(
    db: Session,
    *,
    hours: int = 24,
    min_opportunity: float | None = None,
    workspace_id: UUID | None = None,
) -> DailyBriefingData:
    settings = get_settings()
    window_hours = min(max(hours, 1), 168)
    opportunity_threshold = min_opportunity or settings.alert_opportunity_threshold
    generated_at = datetime.now(UTC)
    since = generated_at - timedelta(hours=window_hours)
    files = _load_files(db, workspace_id=workspace_id)

    new_files: list[BriefingItem] = []
    updated_files: list[BriefingItem] = []
    resurrected: list[BriefingItem] = []
    high_opportunity: list[BriefingItem] = []
    risk_or_noise: list[BriefingItem] = []

    for file in files:
        created_at = _ensure_utc(file.created_at)
        if created_at >= since:
            new_files.append(_item(file, "Created inside the briefing window."))

        if _status_changed_to(file, since, LifecycleStatus.RESURRECTED):
            resurrected.append(_item(file, "Lifecycle changed to resurrected in the window."))

        if _has_recent_event(file, since, IntelEventType.EVIDENCE_ADDED) or _has_recent_event(
            file, since, IntelEventType.SCORE_CHANGED
        ):
            if not _status_changed_to(file, since, LifecycleStatus.RESURRECTED):
                updated_files.append(_item(file, "Evidence or scores changed in the window."))

        if _opportunity_crossed(file, since, opportunity_threshold):
            high_opportunity.append(
                _item(file, f"Opportunity score is at or above {opportunity_threshold:.1f}.")
            )

        if (
            (file.risk_score is not None and file.risk_score >= RISK_THRESHOLD)
            or file.status in {LifecycleStatus.NOISE, LifecycleStatus.DEBUNKED}
            or _status_changed_to(file, since, LifecycleStatus.NOISE)
            or _status_changed_to(file, since, LifecycleStatus.DEBUNKED)
        ):
            risk_or_noise.append(_item(file, "Risk/noise threshold or status matched."))

    sections = BriefingSections(
        new_files=_sort_opportunity(new_files),
        updated_files=_sort_opportunity(updated_files),
        resurrected=_sort_opportunity(resurrected),
        high_opportunity=_sort_opportunity(high_opportunity),
        risk_or_noise=_sort_opportunity(risk_or_noise),
    )
    item_count = sum(len(items) for items in sections.model_dump().values())
    overview = (
        f"Window: {window_hours}h. "
        f"{len(sections.new_files)} new files, "
        f"{len(sections.updated_files)} updated files, "
        f"{len(sections.resurrected)} resurrected signals, "
        f"{len(sections.high_opportunity)} high-opportunity files, "
        f"{len(sections.risk_or_noise)} risk/noise candidates."
    )

    return DailyBriefingData(
        meta=BriefingMeta(
            generated_at=generated_at,
            window_hours=window_hours,
            item_count=item_count,
        ),
        overview=overview,
        sections=sections,
        debug={"opportunity_threshold": opportunity_threshold},
    )


def generate_weekly_retrospective(
    db: Session,
    *,
    days: int = 7,
    min_opportunity: float | None = None,
    workspace_id: UUID | None = None,
) -> WeeklyRetrospectiveData:
    settings = get_settings()
    window_days = min(max(days, 1), 31)
    opportunity_threshold = min_opportunity or settings.alert_opportunity_threshold
    generated_at = datetime.now(UTC)
    since = generated_at - timedelta(days=window_days)
    files = _load_files(db, workspace_id=workspace_id)

    changed_files: list[BriefingItem] = []
    resurrected: list[BriefingItem] = []
    verified_or_debunked: list[BriefingItem] = []
    opportunity_gainers: list[BriefingItem] = []
    cooling_or_noise: list[BriefingItem] = []

    for file in files:
        if _has_recent_event(file, since, IntelEventType.STATUS_CHANGED) or _has_recent_event(
            file, since, IntelEventType.SCORE_CHANGED
        ):
            changed_files.append(_item(file, "Status or score changed during the week."))

        if _status_changed_to(file, since, LifecycleStatus.RESURRECTED):
            resurrected.append(_item(file, "Signal resurrected during the week."))

        if _status_changed_to(file, since, LifecycleStatus.VERIFIED) or _status_changed_to(
            file, since, LifecycleStatus.DEBUNKED
        ):
            verified_or_debunked.append(_item(file, "Signal reached a verified or debunked state."))

        if _opportunity_crossed(file, since, opportunity_threshold):
            opportunity_gainers.append(
                _item(file, f"Opportunity is at or above {opportunity_threshold:.1f}.")
            )

        if (
            file.status in {LifecycleStatus.COOLING, LifecycleStatus.NOISE, LifecycleStatus.DEBUNKED}
            or _status_changed_to(file, since, LifecycleStatus.COOLING)
            or _status_changed_to(file, since, LifecycleStatus.NOISE)
            or _status_changed_to(file, since, LifecycleStatus.DEBUNKED)
        ):
            cooling_or_noise.append(_item(file, "Signal cooled, became noise, or was debunked."))

    sections = WeeklyBriefingSections(
        changed_files=_sort_opportunity(changed_files),
        resurrected=_sort_opportunity(resurrected),
        verified_or_debunked=_sort_opportunity(verified_or_debunked),
        opportunity_gainers=_sort_opportunity(opportunity_gainers),
        cooling_or_noise=_sort_opportunity(cooling_or_noise),
    )
    item_count = sum(len(items) for items in sections.model_dump().values())
    overview = (
        f"Window: {window_days}d. "
        f"{len(sections.changed_files)} changed files, "
        f"{len(sections.resurrected)} resurrected signals, "
        f"{len(sections.verified_or_debunked)} verified/debunked files, "
        f"{len(sections.opportunity_gainers)} opportunity gainers, "
        f"{len(sections.cooling_or_noise)} cooling/noise files."
    )

    return WeeklyRetrospectiveData(
        meta=WeeklyBriefingMeta(
            generated_at=generated_at,
            window_days=window_days,
            item_count=item_count,
        ),
        overview=overview,
        sections=sections,
        debug={"opportunity_threshold": opportunity_threshold},
    )

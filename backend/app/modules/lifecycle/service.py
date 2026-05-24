from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import Evidence, IntelEvent, IntelFile, LifecycleSnapshot
from app.models.enums import EvidenceType, IntelEventType, LifecycleStatus
from app.modules.alerts.service import process_lifecycle_alerts
from app.schemas.lifecycle import (
    LifecycleEvaluateData,
    LifecycleEvaluateRequest,
    LifecycleStatusOverrideData,
    LifecycleStatusOverrideRequest,
)

SPREADING_EVIDENCE_THRESHOLD = 3
SPREADING_SOURCE_THRESHOLD = 2
SPREADING_HEAT_THRESHOLD = 5.0
VALIDATING_CREDIBILITY_THRESHOLD = 6.0
VERIFIED_CREDIBILITY_THRESHOLD = 8.0
NOISE_OPPORTUNITY_MAX = 2.0
NOISE_RISK_MIN = 6.0
DEBUNK_RISK_MIN = 7.0
DEBUNK_CREDIBILITY_MAX = 4.0
RESURRECTION_RECENT_DAYS = 1

TERMINAL_STATUSES = {
    LifecycleStatus.VERIFIED,
    LifecycleStatus.DEBUNKED,
    LifecycleStatus.NOISE,
}


@dataclass
class EvaluationContext:
    intel_file: IntelFile
    evidence: list[Evidence]
    now: datetime
    dormancy_days: int


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _days_between(earlier: datetime, later: datetime) -> int:
    return (_ensure_utc(later) - _ensure_utc(earlier)).days


def _score_changes(intel_file: IntelFile) -> dict[str, list[float | None]]:
    return {
        "heat_score": [intel_file.heat_score, intel_file.heat_score],
        "credibility_score": [intel_file.credibility_score, intel_file.credibility_score],
        "opportunity_score": [intel_file.opportunity_score, intel_file.opportunity_score],
        "risk_score": [intel_file.risk_score, intel_file.risk_score],
    }


def _meaningful_recent_evidence(ctx: EvaluationContext) -> list[Evidence]:
    cutoff = _ensure_utc(ctx.now) - timedelta(days=RESURRECTION_RECENT_DAYS)
    if _ensure_utc(ctx.intel_file.last_seen_at) < cutoff:
        return []
    return [item for item in ctx.evidence if item.evidence_type != EvidenceType.FIRST_SEEN]


def propose_transition(ctx: EvaluationContext) -> tuple[LifecycleStatus, str, list[UUID]]:
    intel_file = ctx.intel_file
    evidence = ctx.evidence
    evidence_ids = [item.id for item in evidence]

    if intel_file.status in TERMINAL_STATUSES:
        return intel_file.status, "Terminal status unchanged.", evidence_ids[:1]

    contradiction = [
        item
        for item in evidence
        if item.evidence_type in {EvidenceType.CONTRADICTION, EvidenceType.CORRECTION}
    ]
    if contradiction:
        return (
            LifecycleStatus.DEBUNKED,
            "Contradiction or correction evidence indicates claim disproof.",
            [item.id for item in contradiction],
        )

    if (
        intel_file.risk_score is not None
        and intel_file.risk_score >= DEBUNK_RISK_MIN
        and (intel_file.credibility_score or 0) <= DEBUNK_CREDIBILITY_MAX
    ):
        return (
            LifecycleStatus.DEBUNKED,
            "High risk and low credibility indicate the signal is disproven or misleading.",
            evidence_ids[:1],
        )

    corroboration = [item for item in evidence if item.evidence_type == EvidenceType.CORROBORATION]
    if (intel_file.credibility_score or 0) >= VERIFIED_CREDIBILITY_THRESHOLD and (
        corroboration or intel_file.evidence_count >= 3
    ):
        return (
            LifecycleStatus.VERIFIED,
            "Credibility threshold met with supporting evidence.",
            [item.id for item in corroboration] or evidence_ids[:1],
        )

    noise_evidence = [item for item in evidence if item.evidence_type == EvidenceType.NOISE]
    if noise_evidence:
        return (
            LifecycleStatus.NOISE,
            "Noise evidence attached.",
            [item.id for item in noise_evidence],
        )

    if (intel_file.opportunity_score or 10) <= NOISE_OPPORTUNITY_MAX and (
        intel_file.risk_score or 0
    ) >= NOISE_RISK_MIN:
        return (
            LifecycleStatus.NOISE,
            "Low opportunity and elevated risk indicate noise.",
            evidence_ids[:1],
        )

    if intel_file.status in {LifecycleStatus.DORMANT, LifecycleStatus.ARCHIVED}:
        recent = _meaningful_recent_evidence(ctx)
        if recent:
            return (
                LifecycleStatus.RESURRECTED,
                f"New meaningful evidence appeared after {ctx.dormancy_days} days of inactivity.",
                [item.id for item in recent],
            )
        return intel_file.status, "No resurrection evidence detected.", evidence_ids[:1]

    inactive_days = _days_between(intel_file.last_seen_at, ctx.now)
    if inactive_days >= ctx.dormancy_days:
        return (
            LifecycleStatus.DORMANT,
            f"No meaningful evidence for {ctx.dormancy_days} days.",
            [],
        )

    if (
        intel_file.evidence_count >= SPREADING_EVIDENCE_THRESHOLD
        or intel_file.source_count >= SPREADING_SOURCE_THRESHOLD
        or (intel_file.heat_score or 0) >= SPREADING_HEAT_THRESHOLD
    ):
        return (
            LifecycleStatus.SPREADING,
            "Evidence, source, or heat thresholds crossed.",
            evidence_ids,
        )

    if (intel_file.credibility_score or 0) >= VALIDATING_CREDIBILITY_THRESHOLD and (
        corroboration or intel_file.evidence_count >= 2
    ):
        return (
            LifecycleStatus.VALIDATING,
            "Credibility increased with corroborating evidence.",
            [item.id for item in corroboration] or evidence_ids[:1],
        )

    if intel_file.status == LifecycleStatus.NEW and (intel_file.keywords or intel_file.entities):
        return (
            LifecycleStatus.WATCHING,
            "Signal is trackable with entities or keywords.",
            evidence_ids[:1],
        )

    return intel_file.status, "No lifecycle transition warranted.", evidence_ids[:1]


def evaluate_intel_file(
    db: Session,
    intel_file_id: UUID,
    payload: LifecycleEvaluateRequest,
    *,
    workspace_id: UUID | None = None,
) -> LifecycleEvaluateData:
    intel_file = db.scalar(
        select(IntelFile)
        .options(selectinload(IntelFile.evidence))
        .where(IntelFile.id == intel_file_id)
    )
    if intel_file is None or (workspace_id is not None and intel_file.workspace_id != workspace_id):
        raise ValueError("Intel file not found.")

    settings = get_settings()
    now = _ensure_utc(payload.now or datetime.now(UTC))
    evidence = list(intel_file.evidence)
    ctx = EvaluationContext(
        intel_file=intel_file,
        evidence=evidence,
        now=now,
        dormancy_days=settings.lifecycle_dormancy_days,
    )

    previous_status = intel_file.status
    next_status, reason, evidence_ids = propose_transition(ctx)
    score_changes = _score_changes(intel_file)

    snapshot = LifecycleSnapshot(
        intel_file_id=intel_file.id,
        snapshot_time=now,
        status=next_status,
        heat_score=intel_file.heat_score,
        credibility_score=intel_file.credibility_score,
        opportunity_score=intel_file.opportunity_score,
        risk_score=intel_file.risk_score,
        reason=reason,
    )
    db.add(snapshot)

    if next_status != previous_status:
        intel_file.status = next_status
        event = IntelEvent(
            intel_file_id=intel_file.id,
            event_type=IntelEventType.STATUS_CHANGED,
            event_time=now,
            title=f"Status changed to {next_status.value}",
            description=reason,
            metadata_={
                "previous_status": previous_status.value,
                "next_status": next_status.value,
                "evaluation_reason": payload.reason,
                "evidence_ids": [str(item) for item in evidence_ids],
            },
        )
        db.add(event)
        process_lifecycle_alerts(
            db,
            intel_file,
            previous_status=previous_status,
            next_status=next_status,
            reason=reason,
        )

    db.commit()
    db.refresh(intel_file)

    return LifecycleEvaluateData(
        previous_status=previous_status,
        next_status=next_status,
        reason=reason,
        evidence_ids=evidence_ids,
        score_changes=score_changes,
    )


def override_intel_file_status(
    db: Session,
    intel_file_id: UUID,
    payload: LifecycleStatusOverrideRequest,
    *,
    workspace_id: UUID | None = None,
) -> LifecycleStatusOverrideData:
    intel_file = db.scalar(select(IntelFile).where(IntelFile.id == intel_file_id))
    if intel_file is None or (workspace_id is not None and intel_file.workspace_id != workspace_id):
        raise ValueError("Intel file not found.")

    now = _ensure_utc(payload.now or datetime.now(UTC))
    previous_status = intel_file.status
    next_status = payload.status
    reason = payload.reason.strip()

    snapshot = LifecycleSnapshot(
        intel_file_id=intel_file.id,
        snapshot_time=now,
        status=next_status,
        heat_score=intel_file.heat_score,
        credibility_score=intel_file.credibility_score,
        opportunity_score=intel_file.opportunity_score,
        risk_score=intel_file.risk_score,
        reason=f"Manual override: {reason}",
    )
    db.add(snapshot)

    if previous_status != next_status:
        intel_file.status = next_status
        event = IntelEvent(
            intel_file_id=intel_file.id,
            event_type=IntelEventType.STATUS_CHANGED,
            event_time=now,
            title=f"Status manually changed to {next_status.value}",
            description=reason,
            metadata_={
                "previous_status": previous_status.value,
                "next_status": next_status.value,
                "override": True,
            },
        )
        db.add(event)
        process_lifecycle_alerts(
            db,
            intel_file,
            previous_status=previous_status,
            next_status=next_status,
            reason=reason,
        )

    db.commit()
    return LifecycleStatusOverrideData(
        previous_status=previous_status,
        next_status=next_status,
        reason=reason,
    )

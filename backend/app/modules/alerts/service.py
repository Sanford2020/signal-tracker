from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import AlertEvent, IntelFile
from app.models.enums import AlertSeverity, AlertStatus, AlertType, LifecycleStatus
from app.schemas.alerts import AlertListData, AlertSummary, AlertUpdateRequest

ACTIVE_DEDUPE_STATUSES = {
    AlertStatus.PENDING,
    AlertStatus.SENT,
    AlertStatus.ACKNOWLEDGED,
}


def _encode_message(dedupe_key: str, text: str) -> str:
    return f"{dedupe_key}|{text}"


def display_message(raw: str) -> str:
    if "|" in raw:
        return raw.split("|", 1)[1]
    return raw


def _alert_exists(db: Session, intel_file_id: UUID, dedupe_key: str) -> bool:
    existing = db.scalar(
        select(AlertEvent).where(
            AlertEvent.intel_file_id == intel_file_id,
            AlertEvent.message.like(f"{dedupe_key}|%"),
            AlertEvent.status.in_(ACTIVE_DEDUPE_STATUSES),
        )
    )
    return existing is not None


def create_alert(
    db: Session,
    *,
    intel_file_id: UUID,
    alert_type: AlertType,
    message: str,
    dedupe_key: str,
    severity: AlertSeverity = AlertSeverity.WATCH,
) -> AlertEvent | None:
    if _alert_exists(db, intel_file_id, dedupe_key):
        return None

    alert = AlertEvent(
        intel_file_id=intel_file_id,
        alert_type=alert_type,
        severity=severity,
        message=_encode_message(dedupe_key, message),
        status=AlertStatus.PENDING,
    )
    db.add(alert)
    return alert


def process_lifecycle_alerts(
    db: Session,
    intel_file: IntelFile,
    *,
    previous_status: LifecycleStatus,
    next_status: LifecycleStatus,
    reason: str,
) -> list[AlertEvent]:
    if previous_status == next_status:
        return []

    created: list[AlertEvent] = []
    dedupe_base = f"lifecycle:{previous_status.value}->{next_status.value}"

    if previous_status == LifecycleStatus.DORMANT and next_status == LifecycleStatus.RESURRECTED:
        alert = create_alert(
            db,
            intel_file_id=intel_file.id,
            alert_type=AlertType.RESURRECTED,
            dedupe_key=dedupe_base,
            severity=AlertSeverity.IMPORTANT,
            message=f"Signal resurrected: {intel_file.title}. {reason}",
        )
        if alert:
            created.append(alert)
    elif next_status == LifecycleStatus.VERIFIED:
        alert = create_alert(
            db,
            intel_file_id=intel_file.id,
            alert_type=AlertType.VERIFIED,
            dedupe_key=dedupe_base,
            severity=AlertSeverity.IMPORTANT,
            message=f"Signal verified: {intel_file.title}. {reason}",
        )
        if alert:
            created.append(alert)
    elif next_status == LifecycleStatus.DEBUNKED:
        alert = create_alert(
            db,
            intel_file_id=intel_file.id,
            alert_type=AlertType.DEBUNKED,
            dedupe_key=dedupe_base,
            severity=AlertSeverity.URGENT,
            message=f"Signal debunked: {intel_file.title}. {reason}",
        )
        if alert:
            created.append(alert)

    return created


def process_score_alerts(
    db: Session,
    intel_file: IntelFile,
    score_changes: dict[str, list[float | None]],
) -> list[AlertEvent]:
    settings = get_settings()
    created: list[AlertEvent] = []

    prev_heat, new_heat = score_changes.get("heat_score", [None, None])
    if prev_heat is not None and new_heat is not None:
        if new_heat - prev_heat >= settings.alert_heat_spike_min:
            alert = create_alert(
                db,
                intel_file_id=intel_file.id,
                alert_type=AlertType.HEAT_SPIKE,
                dedupe_key=f"score:heat:{prev_heat}->{new_heat}",
                severity=AlertSeverity.WATCH,
                message=(
                    f"Heat spike on {intel_file.title}: "
                    f"{prev_heat:.1f} → {new_heat:.1f}."
                ),
            )
            if alert:
                created.append(alert)

    prev_cred, new_cred = score_changes.get("credibility_score", [None, None])
    if prev_cred is not None and new_cred is not None:
        if new_cred - prev_cred >= settings.alert_credibility_increase_min:
            alert = create_alert(
                db,
                intel_file_id=intel_file.id,
                alert_type=AlertType.CREDIBILITY_UP,
                dedupe_key=f"score:credibility:{prev_cred}->{new_cred}",
                severity=AlertSeverity.WATCH,
                message=(
                    f"Credibility increased on {intel_file.title}: "
                    f"{prev_cred:.1f} → {new_cred:.1f}."
                ),
            )
            if alert:
                created.append(alert)

    prev_risk, new_risk = score_changes.get("risk_score", [None, None])
    if prev_risk is not None and new_risk is not None:
        if prev_risk < settings.alert_risk_threshold <= new_risk:
            alert = create_alert(
                db,
                intel_file_id=intel_file.id,
                alert_type=AlertType.RISK_UP,
                dedupe_key=f"score:risk_cross:{settings.alert_risk_threshold}",
                severity=AlertSeverity.IMPORTANT,
                message=(
                    f"Risk threshold crossed on {intel_file.title}: "
                    f"now {new_risk:.1f} (threshold {settings.alert_risk_threshold:.1f})."
                ),
            )
            if alert:
                created.append(alert)

    prev_opp, new_opp = score_changes.get("opportunity_score", [None, None])
    if prev_opp is not None and new_opp is not None:
        threshold = settings.alert_opportunity_threshold
        if prev_opp < threshold <= new_opp:
            alert = create_alert(
                db,
                intel_file_id=intel_file.id,
                alert_type=AlertType.OPPORTUNITY_UP,
                dedupe_key=f"score:opportunity_cross:{threshold}",
                severity=AlertSeverity.IMPORTANT,
                message=(
                    f"High opportunity on {intel_file.title}: "
                    f"score crossed {threshold:.1f} (now {new_opp:.1f})."
                ),
            )
            if alert:
                created.append(alert)

    return created


def list_alerts(
    db: Session,
    *,
    status: AlertStatus | None = None,
    alert_type: AlertType | None = None,
    severity: AlertSeverity | None = None,
) -> AlertListData:
    query = (
        select(AlertEvent)
        .options(selectinload(AlertEvent.intel_file))
        .order_by(AlertEvent.created_at.desc())
    )
    count_query = select(func.count()).select_from(AlertEvent)

    if status is not None:
        query = query.where(AlertEvent.status == status)
        count_query = count_query.where(AlertEvent.status == status)
    if alert_type is not None:
        query = query.where(AlertEvent.alert_type == alert_type)
        count_query = count_query.where(AlertEvent.alert_type == alert_type)
    if severity is not None:
        query = query.where(AlertEvent.severity == severity)
        count_query = count_query.where(AlertEvent.severity == severity)

    total = db.scalar(count_query) or 0
    items = db.scalars(query).all()

    return AlertListData(
        items=[
            AlertSummary(
                id=item.id,
                intel_file_id=item.intel_file_id,
                intel_file_title=item.intel_file.title if item.intel_file else "Unknown file",
                alert_type=item.alert_type,
                severity=item.severity,
                message=display_message(item.message),
                status=item.status,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
    )


def update_alert_status(
    db: Session,
    alert_id: UUID,
    payload: AlertUpdateRequest,
) -> AlertSummary:
    if payload.status not in {AlertStatus.ACKNOWLEDGED, AlertStatus.DISMISSED}:
        raise ValueError("Only acknowledged or dismissed status updates are supported.")

    alert = db.scalar(
        select(AlertEvent)
        .options(selectinload(AlertEvent.intel_file))
        .where(AlertEvent.id == alert_id)
    )
    if alert is None:
        raise ValueError("Alert not found.")

    alert.status = payload.status
    db.commit()
    db.refresh(alert)

    return AlertSummary(
        id=alert.id,
        intel_file_id=alert.intel_file_id,
        intel_file_title=alert.intel_file.title if alert.intel_file else "Unknown file",
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=display_message(alert.message),
        status=alert.status,
        created_at=alert.created_at,
    )

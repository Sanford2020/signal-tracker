from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    AlertEvent,
    IntelFile,
    NotificationChannelConfig,
    NotificationDeliveryAttempt,
)
from app.models.enums import AlertStatus
from app.schemas.notifications import (
    NotificationChannelCreateData,
    NotificationChannelCreateRequest,
    NotificationChannelListData,
    NotificationDeliveryRunData,
    NotificationDeliveryRunRequest,
)


def create_notification_channel(
    db: Session,
    payload: NotificationChannelCreateRequest,
    *,
    workspace_id,
) -> NotificationChannelCreateData:
    channel = NotificationChannelConfig(
        workspace_id=workspace_id,
        name=payload.name.strip(),
        channel=payload.channel,
        target=payload.target.strip(),
        enabled=payload.enabled,
        config=payload.config,
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return NotificationChannelCreateData(item=channel)


def list_notification_channels(db: Session, *, workspace_id) -> NotificationChannelListData:
    query = select(NotificationChannelConfig).order_by(NotificationChannelConfig.created_at.desc())
    if workspace_id is not None:
        query = query.where(NotificationChannelConfig.workspace_id == workspace_id)
    items = db.scalars(query).all()
    return NotificationChannelListData(items=list(items), total=len(items))


def run_notification_delivery(
    db: Session,
    payload: NotificationDeliveryRunRequest,
    *,
    workspace_id,
) -> NotificationDeliveryRunData:
    channels_query = select(NotificationChannelConfig).where(NotificationChannelConfig.enabled.is_(True))
    if workspace_id is not None:
        channels_query = channels_query.where(NotificationChannelConfig.workspace_id == workspace_id)
    channels = db.scalars(channels_query).all()

    alerts_query = (
        select(AlertEvent)
        .options(selectinload(AlertEvent.intel_file))
        .where(AlertEvent.status == AlertStatus.PENDING)
        .order_by(AlertEvent.created_at.asc(), AlertEvent.id.asc())
        .limit(payload.limit)
    )
    alerts = db.scalars(alerts_query).all()

    attempts: list[NotificationDeliveryAttempt] = []
    skipped_count = 0
    for alert in alerts:
        alert_workspace_id = alert.intel_file.workspace_id if alert.intel_file else None
        if workspace_id is not None and alert_workspace_id != workspace_id:
            skipped_count += 1
            continue

        delivered_for_alert = False
        for channel in channels:
            existing = db.scalar(
                select(NotificationDeliveryAttempt).where(
                    NotificationDeliveryAttempt.alert_event_id == alert.id,
                    NotificationDeliveryAttempt.channel_config_id == channel.id,
                )
            )
            if existing is not None:
                skipped_count += 1
                continue
            attempt = NotificationDeliveryAttempt(
                alert_event_id=alert.id,
                channel_config_id=channel.id,
                status="sent",
                provider_message_id=f"mock-{alert.id}-{channel.id}",
                payload={
                    "channel": channel.channel,
                    "target": channel.target,
                    "message": alert.message,
                },
            )
            db.add(attempt)
            attempts.append(attempt)
            delivered_for_alert = True
        if delivered_for_alert:
            alert.status = AlertStatus.SENT

    db.commit()
    for attempt in attempts:
        db.refresh(attempt)
    return NotificationDeliveryRunData(
        checked_alert_count=len(alerts),
        delivered_count=len(attempts),
        skipped_count=skipped_count,
        attempts=attempts,
    )

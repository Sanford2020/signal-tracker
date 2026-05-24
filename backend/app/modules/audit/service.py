import csv
import io
import json
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AuditEvent
from app.schemas.audit import AuditEventListData, AuditEventRead


def record_audit_event(
    db: Session,
    *,
    action: str,
    workspace_id: UUID | None = None,
    actor_email: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        workspace_id=workspace_id,
        actor_email=actor_email.strip().lower() if actor_email else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata_=metadata,
    )
    db.add(event)
    return event


def list_audit_events(
    db: Session,
    *,
    workspace_id: UUID,
    page: int = 1,
    page_size: int = 50,
) -> AuditEventListData:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    query = (
        select(AuditEvent)
        .where(AuditEvent.workspace_id == workspace_id)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
    )
    total = db.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.workspace_id == workspace_id)) or 0
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return AuditEventListData(
        items=[
            AuditEventRead(
                id=item.id,
                workspace_id=item.workspace_id,
                actor_email=item.actor_email,
                action=item.action,
                target_type=item.target_type,
                target_id=item.target_id,
                metadata=item.metadata_,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
    )


def export_audit_events_csv(db: Session, *, workspace_id: UUID) -> str:
    events = db.scalars(
        select(AuditEvent)
        .where(AuditEvent.workspace_id == workspace_id)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
    ).all()
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "created_at",
            "actor_email",
            "action",
            "target_type",
            "target_id",
            "metadata",
        ],
    )
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "created_at": event.created_at.isoformat(),
                "actor_email": event.actor_email or "",
                "action": event.action,
                "target_type": event.target_type or "",
                "target_id": event.target_id or "",
                "metadata": json.dumps(event.metadata_ or {}, ensure_ascii=True, sort_keys=True),
            }
        )
    return buffer.getvalue()

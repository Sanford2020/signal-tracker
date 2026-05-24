from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AuditEventRead(BaseModel):
    id: UUID
    workspace_id: UUID | None
    actor_email: str | None
    action: str
    target_type: str | None
    target_id: str | None
    metadata: dict[str, Any] | None = None
    created_at: datetime


class AuditEventListData(BaseModel):
    items: list[AuditEventRead]
    total: int

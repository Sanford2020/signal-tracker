from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationChannelCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    channel: str = Field(pattern="^(in_app|email|webhook|feishu|telegram)$")
    target: str = Field(min_length=1, max_length=2048)
    enabled: bool = True
    config: dict[str, Any] | None = None


class NotificationChannelRead(BaseModel):
    id: UUID
    workspace_id: UUID | None
    name: str
    channel: str
    target: str
    enabled: bool
    config: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationChannelListData(BaseModel):
    items: list[NotificationChannelRead]
    total: int


class NotificationChannelCreateData(BaseModel):
    item: NotificationChannelRead


class NotificationDeliveryAttemptRead(BaseModel):
    id: UUID
    alert_event_id: UUID
    channel_config_id: UUID
    status: str
    provider_message_id: str | None
    error: str | None
    payload: dict[str, Any] | None
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationDeliveryRunRequest(BaseModel):
    limit: int = Field(50, ge=1, le=500)


class NotificationDeliveryRunData(BaseModel):
    checked_alert_count: int
    delivered_count: int
    skipped_count: int
    attempts: list[NotificationDeliveryAttemptRead]

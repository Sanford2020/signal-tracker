from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AlertSeverity, AlertStatus, AlertType


class AlertUpdateRequest(BaseModel):
    status: AlertStatus


class AlertSummary(BaseModel):
    id: UUID
    intel_file_id: UUID
    intel_file_title: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    status: AlertStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertListData(BaseModel):
    items: list[AlertSummary]
    total: int

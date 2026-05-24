import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AlertChannel, AlertSeverity, AlertStatus, AlertType


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intel_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intel_files.id", ondelete="CASCADE"), nullable=False
    )
    alert_type: Mapped[AlertType] = mapped_column(
        Enum(AlertType, name="alert_type_enum", native_enum=False),
        nullable=False,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity_enum", native_enum=False),
        nullable=False,
        default=AlertSeverity.WATCH,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status_enum", native_enum=False),
        nullable=False,
        default=AlertStatus.PENDING,
    )
    channel: Mapped[AlertChannel] = mapped_column(
        Enum(AlertChannel, name="alert_channel_enum", native_enum=False),
        nullable=False,
        default=AlertChannel.IN_APP,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    intel_file: Mapped["IntelFile"] = relationship(back_populates="alerts")


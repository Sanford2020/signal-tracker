import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import LifecycleStatus


class LifecycleSnapshot(Base):
    __tablename__ = "lifecycle_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intel_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intel_files.id", ondelete="CASCADE"), nullable=False
    )
    snapshot_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[LifecycleStatus] = mapped_column(
        Enum(LifecycleStatus, name="snapshot_lifecycle_status_enum", native_enum=False),
        nullable=False,
    )
    heat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    credibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    intel_file: Mapped["IntelFile"] = relationship(back_populates="lifecycle_snapshots")


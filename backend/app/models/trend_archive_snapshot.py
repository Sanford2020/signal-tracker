import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import LifecycleStatus


class TrendArchiveSnapshot(Base):
    __tablename__ = "trend_archive_snapshots"
    __table_args__ = (
        UniqueConstraint("intel_file_id", "archive_date", name="uq_trend_archive_file_date"),
        Index("ix_trend_archive_snapshots_archive_date", "archive_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intel_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intel_files.id", ondelete="CASCADE"), nullable=False
    )
    archive_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[LifecycleStatus] = mapped_column(
        Enum(LifecycleStatus, name="trend_archive_lifecycle_status_enum", native_enum=False),
        nullable=False,
    )
    heat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    credibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    intel_file: Mapped["IntelFile"] = relationship(back_populates="trend_archive_snapshots")

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.enums import LifecycleStatus, SignalType


class IntelFile(Base):
    __tablename__ = "intel_files"
    __table_args__ = (
        Index("ix_intel_files_status", "status"),
        Index("ix_intel_files_last_seen_at", "last_seen_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    thesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LifecycleStatus] = mapped_column(
        Enum(LifecycleStatus, name="lifecycle_status_enum", native_enum=False),
        nullable=False,
        default=LifecycleStatus.NEW,
    )
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    primary_signal_type: Mapped[SignalType | None] = mapped_column(
        Enum(SignalType, name="intel_signal_type_enum", native_enum=False),
        nullable=True,
    )
    entities: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    heat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    credibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    opportunity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    owner_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    evidence: Mapped[list["Evidence"]] = relationship(back_populates="intel_file")
    events: Mapped[list["IntelEvent"]] = relationship(back_populates="intel_file")
    lifecycle_snapshots: Mapped[list["LifecycleSnapshot"]] = relationship(
        back_populates="intel_file"
    )
    alerts: Mapped[list["AlertEvent"]] = relationship(back_populates="intel_file")
    tracking_queries: Mapped[list["TrackingQuery"]] = relationship(back_populates="intel_file")
    match_suggestions: Mapped[list["MatchSuggestion"]] = relationship(back_populates="intel_file")
    trend_archive_snapshots: Mapped[list["TrendArchiveSnapshot"]] = relationship(back_populates="intel_file")
    comments: Mapped[list["IntelFileComment"]] = relationship(back_populates="intel_file")

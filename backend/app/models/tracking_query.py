import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base


class TrackingQuery(Base):
    __tablename__ = "tracking_queries"
    __table_args__ = (
        UniqueConstraint("intel_file_id", "normalized_query", name="uq_tracking_queries_file_query"),
        Index("ix_tracking_queries_enabled", "enabled"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intel_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intel_files.id", ondelete="CASCADE"), nullable=False
    )
    query: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_query: Mapped[str] = mapped_column(String(512), nullable=False)
    source_hint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    intel_file: Mapped["IntelFile"] = relationship(back_populates="tracking_queries")

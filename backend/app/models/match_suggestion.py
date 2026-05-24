import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MatchSuggestion(Base):
    __tablename__ = "match_suggestions"
    __table_args__ = (
        UniqueConstraint(
            "intel_file_id",
            "source_check_result_id",
            name="uq_match_suggestions_file_result",
        ),
        Index("ix_match_suggestions_intel_file_status", "intel_file_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intel_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intel_files.id", ondelete="CASCADE"), nullable=False
    )
    source_check_result_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_check_results.id", ondelete="CASCADE"), nullable=False
    )
    suggested_evidence_type: Mapped[str] = mapped_column(String(64), nullable=False, default="follow_up")
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    intel_file: Mapped["IntelFile"] = relationship(back_populates="match_suggestions")
    source_check_result: Mapped["SourceCheckResult"] = relationship(back_populates="match_suggestions")

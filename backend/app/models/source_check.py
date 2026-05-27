import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base


class SourceCheckRun(Base):
    __tablename__ = "source_check_runs"
    __table_args__ = (
        Index("ix_source_check_runs_started_at", "started_at"),
        Index("ix_source_check_runs_workspace_started", "workspace_id", "started_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    checked_query_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    results: Mapped[list["SourceCheckResult"]] = relationship(back_populates="run")


class SourceCheckResult(Base):
    __tablename__ = "source_check_results"
    __table_args__ = (
        Index("ix_source_check_results_tracking_query_id", "tracking_query_id"),
        Index("ix_source_check_results_checked_at", "checked_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("source_check_runs.id", ondelete="CASCADE"), nullable=False
    )
    tracking_query_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tracking_queries.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_hint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    run: Mapped["SourceCheckRun"] = relationship(back_populates="results")
    tracking_query: Mapped["TrackingQuery"] = relationship()
    match_suggestions: Mapped[list["MatchSuggestion"]] = relationship(back_populates="source_check_result")

    @property
    def intel_file_id(self) -> uuid.UUID:
        return self.tracking_query.intel_file_id

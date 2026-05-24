import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.enums import SignalType


class SignalAnalysis(Base):
    __tablename__ = "signal_analyses"
    __table_args__ = (UniqueConstraint("raw_item_id", name="uq_signal_analyses_raw_item_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    raw_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("raw_items.id", ondelete="CASCADE"), nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    signal_type: Mapped[SignalType] = mapped_column(
        Enum(SignalType, name="signal_type_enum", native_enum=False),
        nullable=False,
    )
    entities: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    claims: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    suggested_tracking_queries: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    opportunity_types: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    novelty_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    credibility_hint: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_hint: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    raw_item: Mapped["RawItem"] = relationship(back_populates="signal_analysis")


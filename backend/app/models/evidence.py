import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AttachedBy, EvidenceType


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = (
        UniqueConstraint("intel_file_id", "raw_item_id", name="uq_evidence_file_raw_item"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intel_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("intel_files.id", ondelete="CASCADE"), nullable=False
    )
    raw_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("raw_items.id", ondelete="RESTRICT"), nullable=False
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="evidence_type_enum", native_enum=False),
        nullable=False,
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    attached_by: Mapped[AttachedBy] = mapped_column(
        Enum(AttachedBy, name="attached_by_enum", native_enum=False),
        nullable=False,
        default=AttachedBy.SYSTEM,
    )
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    attached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    intel_file: Mapped["IntelFile"] = relationship(back_populates="evidence")
    raw_item: Mapped["RawItem"] = relationship(back_populates="evidence_links")


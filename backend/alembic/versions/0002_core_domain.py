"""Core domain tables for Signal Tracker MVP."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_core_domain"
down_revision: Union[str, None] = "0001_scaffold"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("trust_tier", sa.Integer(), nullable=False),
        sa.Column("fetch_interval_minutes", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("license_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "raw_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_hash", name="uq_raw_items_content_hash"),
    )
    op.create_index("ix_raw_items_source_id", "raw_items", ["source_id"])
    op.create_index("ix_raw_items_captured_at", "raw_items", ["captured_at"])

    op.create_table(
        "signal_analyses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("raw_item_id", sa.Uuid(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("signal_type", sa.String(length=32), nullable=False),
        sa.Column("entities", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("claims", sa.JSON(), nullable=False),
        sa.Column("novelty_score", sa.Float(), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("credibility_hint", sa.Float(), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("prompt_version", sa.String(length=64), nullable=True),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["raw_item_id"], ["raw_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("raw_item_id", name="uq_signal_analyses_raw_item_id"),
    )

    op.create_table(
        "intel_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("thesis", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("primary_signal_type", sa.String(length=32), nullable=True),
        sa.Column("entities", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("evidence_count", sa.Integer(), nullable=False),
        sa.Column("heat_score", sa.Float(), nullable=True),
        sa.Column("credibility_score", sa.Float(), nullable=True),
        sa.Column("opportunity_score", sa.Float(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("owner_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_intel_files_status", "intel_files", ["status"])
    op.create_index("ix_intel_files_last_seen_at", "intel_files", ["last_seen_at"])

    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("raw_item_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_type", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("attached_by", sa.String(length=16), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("attached_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["raw_item_id"], ["raw_items.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("intel_file_id", "raw_item_id", name="uq_evidence_file_raw_item"),
    )

    op.create_table(
        "intel_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_evidence_id", sa.Uuid(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_evidence_id"], ["evidence.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lifecycle_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("heat_score", sa.Float(), nullable=True),
        sa.Column("credibility_score", sa.Float(), nullable=True),
        sa.Column("opportunity_score", sa.Float(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "alert_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("alert_type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("channel", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("alert_events")
    op.drop_table("lifecycle_snapshots")
    op.drop_table("intel_events")
    op.drop_table("evidence")
    op.drop_index("ix_intel_files_last_seen_at", table_name="intel_files")
    op.drop_index("ix_intel_files_status", table_name="intel_files")
    op.drop_table("intel_files")
    op.drop_table("signal_analyses")
    op.drop_index("ix_raw_items_captured_at", table_name="raw_items")
    op.drop_index("ix_raw_items_source_id", table_name="raw_items")
    op.drop_table("raw_items")
    op.drop_table("sources")

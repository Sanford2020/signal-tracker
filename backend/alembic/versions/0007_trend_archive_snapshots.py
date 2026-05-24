"""trend archive snapshots

Revision ID: 0007_trend_archive_snapshots
Revises: 0006_match_suggestions
Create Date: 2026-05-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_trend_archive_snapshots"
down_revision: str | None = "0006_match_suggestions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "trend_archive_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("archive_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("heat_score", sa.Float(), nullable=True),
        sa.Column("credibility_score", sa.Float(), nullable=True),
        sa.Column("opportunity_score", sa.Float(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("evidence_count", sa.Integer(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("intel_file_id", "archive_date", name="uq_trend_archive_file_date"),
    )
    op.create_index(
        "ix_trend_archive_snapshots_archive_date",
        "trend_archive_snapshots",
        ["archive_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_trend_archive_snapshots_archive_date", table_name="trend_archive_snapshots")
    op.drop_table("trend_archive_snapshots")

"""tracking queries

Revision ID: 0004_tracking_queries
Revises: 0003_intake_extraction_fields
Create Date: 2026-05-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_tracking_queries"
down_revision: str | None = "0003_intake_extraction_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tracking_queries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("query", sa.String(length=512), nullable=False),
        sa.Column("normalized_query", sa.String(length=512), nullable=False),
        sa.Column("source_hint", sa.String(length=64), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("intel_file_id", "normalized_query", name="uq_tracking_queries_file_query"),
    )
    op.create_index("ix_tracking_queries_enabled", "tracking_queries", ["enabled"])


def downgrade() -> None:
    op.drop_index("ix_tracking_queries_enabled", table_name="tracking_queries")
    op.drop_table("tracking_queries")

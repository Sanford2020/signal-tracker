"""source checks

Revision ID: 0005_source_checks
Revises: 0004_tracking_queries
Create Date: 2026-05-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_source_checks"
down_revision: str | None = "0004_tracking_queries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "source_check_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("checked_query_count", sa.Integer(), nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_check_runs_started_at", "source_check_runs", ["started_at"])
    op.create_table(
        "source_check_results",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("tracking_query_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("source_hint", sa.String(length=64), nullable=True),
        sa.Column("raw", sa.JSON(), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["source_check_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tracking_query_id"], ["tracking_queries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_check_results_tracking_query_id", "source_check_results", ["tracking_query_id"])
    op.create_index("ix_source_check_results_checked_at", "source_check_results", ["checked_at"])


def downgrade() -> None:
    op.drop_index("ix_source_check_results_checked_at", table_name="source_check_results")
    op.drop_index("ix_source_check_results_tracking_query_id", table_name="source_check_results")
    op.drop_table("source_check_results")
    op.drop_index("ix_source_check_runs_started_at", table_name="source_check_runs")
    op.drop_table("source_check_runs")

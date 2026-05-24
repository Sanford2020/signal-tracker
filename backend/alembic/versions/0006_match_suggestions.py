"""match suggestions

Revision ID: 0006_match_suggestions
Revises: 0005_source_checks
Create Date: 2026-05-23 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_match_suggestions"
down_revision: str | None = "0005_source_checks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "match_suggestions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("source_check_result_id", sa.Uuid(), nullable=False),
        sa.Column("suggested_evidence_type", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_check_result_id"], ["source_check_results.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("intel_file_id", "source_check_result_id", name="uq_match_suggestions_file_result"),
    )
    op.create_index(
        "ix_match_suggestions_intel_file_status",
        "match_suggestions",
        ["intel_file_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_match_suggestions_intel_file_status", table_name="match_suggestions")
    op.drop_table("match_suggestions")

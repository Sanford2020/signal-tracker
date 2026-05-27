"""intel file saved views

Revision ID: 0015_intel_file_saved_views
Revises: 0014_source_check_run_workspace
Create Date: 2026-05-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015_intel_file_saved_views"
down_revision: str | None = "0014_source_check_run_workspace"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "intel_file_saved_views",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=False),
        sa.Column("created_by_email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "slug", name="uq_intel_file_saved_views_workspace_slug"),
    )
    op.create_index(
        "ix_intel_file_saved_views_workspace_updated",
        "intel_file_saved_views",
        ["workspace_id", "updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_intel_file_saved_views_workspace_updated", table_name="intel_file_saved_views")
    op.drop_table("intel_file_saved_views")

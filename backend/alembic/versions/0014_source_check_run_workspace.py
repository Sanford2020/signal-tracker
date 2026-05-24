"""source check run workspace scope

Revision ID: 0014_source_check_run_workspace
Revises: 0013_audit_events
Create Date: 2026-05-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014_source_check_run_workspace"
down_revision: str | None = "0013_audit_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("source_check_runs") as batch_op:
        batch_op.add_column(sa.Column("workspace_id", sa.Uuid(), nullable=True))
        batch_op.create_foreign_key(
            "fk_source_check_runs_workspace_id",
            "workspaces",
            ["workspace_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index(
        "ix_source_check_runs_workspace_started",
        "source_check_runs",
        ["workspace_id", "started_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_source_check_runs_workspace_started", table_name="source_check_runs")
    with op.batch_alter_table("source_check_runs") as batch_op:
        batch_op.drop_constraint("fk_source_check_runs_workspace_id", type_="foreignkey")
        batch_op.drop_column("workspace_id")

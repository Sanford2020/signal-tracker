"""auth workspaces

Revision ID: 0008_auth_workspaces
Revises: 0007_trend_archive_snapshots
Create Date: 2026-05-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_auth_workspaces"
down_revision: str | None = "0007_trend_archive_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "workspaces",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "workspace_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_memberships_workspace_user"),
    )
    with op.batch_alter_table("raw_items") as batch_op:
        batch_op.add_column(sa.Column("workspace_id", sa.Uuid(), nullable=True))
        batch_op.create_foreign_key("fk_raw_items_workspace_id", "workspaces", ["workspace_id"], ["id"], ondelete="SET NULL")
    with op.batch_alter_table("intel_files") as batch_op:
        batch_op.add_column(sa.Column("workspace_id", sa.Uuid(), nullable=True))
        batch_op.create_foreign_key("fk_intel_files_workspace_id", "workspaces", ["workspace_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    with op.batch_alter_table("intel_files") as batch_op:
        batch_op.drop_constraint("fk_intel_files_workspace_id", type_="foreignkey")
        batch_op.drop_column("workspace_id")
    with op.batch_alter_table("raw_items") as batch_op:
        batch_op.drop_constraint("fk_raw_items_workspace_id", type_="foreignkey")
        batch_op.drop_column("workspace_id")
    op.drop_table("workspace_memberships")
    op.drop_table("workspaces")
    op.drop_table("users")

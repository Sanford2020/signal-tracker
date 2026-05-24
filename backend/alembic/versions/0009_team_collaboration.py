"""team collaboration

Revision ID: 0009_team_collaboration
Revises: 0008_auth_workspaces
Create Date: 2026-05-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_team_collaboration"
down_revision: str | None = "0008_auth_workspaces"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("intel_files") as batch_op:
        batch_op.add_column(sa.Column("owner_user_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("review_note", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_foreign_key("fk_intel_files_owner_user_id", "users", ["owner_user_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "intel_file_comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intel_file_id", sa.Uuid(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["intel_file_id"], ["intel_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("intel_file_comments")
    with op.batch_alter_table("intel_files") as batch_op:
        batch_op.drop_constraint("fk_intel_files_owner_user_id", type_="foreignkey")
        batch_op.drop_column("last_reviewed_at")
        batch_op.drop_column("review_note")
        batch_op.drop_column("owner_user_id")

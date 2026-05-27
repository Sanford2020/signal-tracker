"""saved view usage metadata

Revision ID: 0017_saved_view_usage_metadata
Revises: 0016_saved_view_default
Create Date: 2026-05-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017_saved_view_usage_metadata"
down_revision: str | None = "0016_saved_view_default"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "intel_file_saved_views",
        sa.Column("description", sa.String(length=240), server_default="", nullable=False),
    )
    op.add_column("intel_file_saved_views", sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("intel_file_saved_views", "last_used_at")
    op.drop_column("intel_file_saved_views", "description")

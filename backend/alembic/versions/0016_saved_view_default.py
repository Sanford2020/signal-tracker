"""saved view default

Revision ID: 0016_saved_view_default
Revises: 0015_intel_file_saved_views
Create Date: 2026-05-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0016_saved_view_default"
down_revision: str | None = "0015_intel_file_saved_views"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "intel_file_saved_views",
        sa.Column("is_default", sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("intel_file_saved_views", "is_default")

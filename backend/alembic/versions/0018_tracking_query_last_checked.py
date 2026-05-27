"""tracking query last checked

Revision ID: 0018_tracking_query_last_checked
Revises: 0017_saved_view_usage_metadata
Create Date: 2026-05-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0018_tracking_query_last_checked"
down_revision: str | None = "0017_saved_view_usage_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tracking_queries", sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_tracking_queries_last_checked", "tracking_queries", ["last_checked_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tracking_queries_last_checked", table_name="tracking_queries")
    op.drop_column("tracking_queries", "last_checked_at")

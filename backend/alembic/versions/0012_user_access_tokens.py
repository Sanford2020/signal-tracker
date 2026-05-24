"""user access tokens

Revision ID: 0012_user_access_tokens
Revises: 0011_usage_events
Create Date: 2026-05-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012_user_access_tokens"
down_revision: str | None = "0011_usage_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("access_token_hash", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("access_token_hint", sa.String(length=16), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "access_token_hint")
    op.drop_column("users", "access_token_hash")

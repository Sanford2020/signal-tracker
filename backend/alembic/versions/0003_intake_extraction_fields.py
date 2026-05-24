"""Align domain model with URL-only intake and full AI extraction contract."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_intake_extraction_fields"
down_revision: Union[str, None] = "0002_core_domain"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("raw_items", schema=None) as batch_op:
        batch_op.alter_column("content", existing_type=sa.Text(), nullable=True)

    op.add_column(
        "signal_analyses",
        sa.Column("suggested_tracking_queries", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "signal_analyses",
        sa.Column("opportunity_types", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column("signal_analyses", sa.Column("risk_hint", sa.Float(), nullable=True))
    op.add_column("signal_analyses", sa.Column("rationale", sa.Text(), nullable=True))

    with op.batch_alter_table("signal_analyses", schema=None) as batch_op:
        batch_op.alter_column("suggested_tracking_queries", server_default=None)
        batch_op.alter_column("opportunity_types", server_default=None)


def downgrade() -> None:
    op.drop_column("signal_analyses", "rationale")
    op.drop_column("signal_analyses", "risk_hint")
    op.drop_column("signal_analyses", "opportunity_types")
    op.drop_column("signal_analyses", "suggested_tracking_queries")

    with op.batch_alter_table("raw_items", schema=None) as batch_op:
        batch_op.alter_column("content", existing_type=sa.Text(), nullable=False)

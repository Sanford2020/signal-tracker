"""Initial scaffold migration (empty).

Domain tables are added in TASK-P1-02.
"""

from typing import Sequence, Union

revision: str = "0001_scaffold"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

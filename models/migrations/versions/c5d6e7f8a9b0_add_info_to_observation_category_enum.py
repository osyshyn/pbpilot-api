"""add INFO to observation_category_enum

Revision ID: c5d6e7f8a9b0
Revises: 9d3e7f1a2b4c
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, Sequence[str], None] = '9d3e7f1a2b4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE observation_category_enum ADD VALUE IF NOT EXISTS 'INFO'"
    )


def downgrade() -> None:
    # PostgreSQL does not support removing a value from an enum easily.
    # Reverting would require creating a new type, migrating data, and
    # dropping the old type. Left as no-op; INFO values remain in DB.
    pass

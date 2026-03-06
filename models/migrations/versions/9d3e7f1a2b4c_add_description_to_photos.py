"""add_description_to_photos

Revision ID: 9d3e7f1a2b4c
Revises: 8c07c784da05
Create Date: 2026-03-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = '9d3e7f1a2b4c'
down_revision: Union[str, Sequence[str], None] = '8c07c784da05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'photos',
        sa.Column(
            'descriptions',
            sa.String(length=1024),
            nullable=True,
            comment='Optional descriptions/caption for the photo',
        ),
    )


def downgrade() -> None:
    op.drop_column('photos', 'descriptions')

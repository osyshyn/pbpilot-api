"""add sample_photos table for multiple photos per sample

Revision ID: d7e8f9a0b1c2
Revises: c5d6e7f8a9b0
Create Date: 2026-03-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'd7e8f9a0b1c2'
down_revision: Union[str, Sequence[str], None] = 'c5d6e7f8a9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sample_photos',
        sa.Column('sample_id', sa.UUID(), nullable=False),
        sa.Column('s3_key', sa.String(length=512), nullable=False),
        sa.Column(
            'descriptions',
            sa.String(length=1024),
            nullable=True,
            comment='Optional descriptions/caption for the photo',
        ),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['sample_id'],
            ['samples.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_sample_photos_sample_id'),
        'sample_photos',
        ['sample_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_sample_photos_sample_id'),
        table_name='sample_photos',
    )
    op.drop_table('sample_photos')

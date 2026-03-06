"""add_status_for_job

Revision ID: 5eab186f1c67
Revises: e52818476f68
Create Date: 2026-02-28 01:45:52.883438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '5eab186f1c67'
down_revision: Union[str, Sequence[str], None] = 'e52818476f68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    job_status_enum = postgresql.ENUM(
        'COMPLETED',
        'IN_PROGRESS',
        'SCHEDULED',
        'AWAITING_RESULTS',
        name='job_status_enum',
    )
    job_status_enum.create(op.get_bind())

    op.add_column(
        'jobs',
        sa.Column(
            'status',
            job_status_enum,
            nullable=False,
            server_default='SCHEDULED',
        ),
    )


def downgrade() -> None:
    op.drop_column('jobs', 'status')

    job_status_enum = postgresql.ENUM(
        'COMPLETED',
        'IN_PROGRESS',
        'SCHEDULED',
        'AWAITING_RESULTS',
        name='job_status_enum',
    )
    job_status_enum.drop(op.get_bind())

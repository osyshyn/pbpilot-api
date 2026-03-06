"""remove_is_day_off_from_company_schedule

Revision ID: a1b2c3d4e5f6
Revises: 1c59a6fc0a09
Create Date: 2026-02-13

Schedule now stores only working days. Days not in the list are implicitly off.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '1c59a6fc0a09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove rows that represent days off (NULL times)
    op.execute(
        "DELETE FROM company_schedules WHERE start_time IS NULL OR end_time IS NULL"
    )
    op.drop_column('company_schedules', 'is_day_off')
    op.alter_column(
        'company_schedules',
        'start_time',
        existing_type=sa.Time(),
        nullable=False,
    )
    op.alter_column(
        'company_schedules',
        'end_time',
        existing_type=sa.Time(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'company_schedules',
        'start_time',
        existing_type=sa.Time(),
        nullable=True,
    )
    op.alter_column(
        'company_schedules',
        'end_time',
        existing_type=sa.Time(),
        nullable=True,
    )
    op.add_column(
        'company_schedules',
        sa.Column('is_day_off', sa.Boolean(), nullable=False, server_default='false'),
    )

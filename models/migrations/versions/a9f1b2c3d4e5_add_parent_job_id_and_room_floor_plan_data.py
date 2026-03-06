"""add_parent_job_id_and_room_floor_plan_data

Revision ID: a9f1b2c3d4e5
Revises: 40add9110cab
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a9f1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = '40add9110cab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'jobs',
        sa.Column(
            'parent_job_id',
            sa.Integer(),
            nullable=True,
            comment='Original job for RETEST inspections',
        ),
    )
    op.create_foreign_key(
        'fk_jobs_parent_job_id',
        'jobs',
        'jobs',
        ['parent_job_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index(
        op.f('ix_jobs_parent_job_id'),
        'jobs',
        ['parent_job_id'],
        unique=False,
    )

    op.add_column(
        'units',
        sa.Column(
            'floor_plan_data',
            postgresql.JSONB(),
            nullable=True,
            comment='Arbitrary JSON data from Flutter for floor plan construction',
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('units', 'floor_plan_data')

    op.drop_index(op.f('ix_jobs_parent_job_id'), table_name='jobs')
    op.drop_constraint('fk_jobs_parent_job_id', 'jobs', type_='foreignkey')
    op.drop_column('jobs', 'parent_job_id')

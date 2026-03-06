"""add_status_for_project

Revision ID: ba7cd107ccbd
Revises: 1142a3c06217
Create Date: 2026-02-19 18:19:54.920963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ba7cd107ccbd'
down_revision: Union[str, Sequence[str], None] = '1142a3c06217'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    project_status_enum = postgresql.ENUM(
        'COMPLETED', 'IN_PROGRESS', 'AWAITING_LAB_RESULTS', 'OVERDUE', 'READY_TO_GENERATE',
        name='project_status_enum'
    )

    project_status_enum.create(op.get_bind())

    op.add_column(
        'projects',
        sa.Column('status', project_status_enum, nullable=False, server_default='IN_PROGRESS')
    )


def downgrade() -> None:
    op.drop_column('projects', 'status')

    project_status_enum = postgresql.ENUM(
        'COMPLETED', 'IN_PROGRESS', 'AWAITING_LAB_RESULTS', 'OVERDUE', 'READY_TO_GENERATE',
        name='project_status_enum'
    )
    project_status_enum.drop(op.get_bind())

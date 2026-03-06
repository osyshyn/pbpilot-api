"""add_unit_id_to_coc_forms

Revision ID: b1c2d3e4f5g6
Revises: a9f1b2c3d4e5
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, Sequence[str], None] = 'a9f1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'coc_forms',
        sa.Column('unit_id', sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        'fk_coc_forms_unit_id',
        'coc_forms',
        'units',
        ['unit_id'],
        ['id'],
        ondelete='CASCADE',
    )
    op.create_index(
        op.f('ix_coc_forms_unit_id'),
        'coc_forms',
        ['unit_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_coc_forms_unit_id'), table_name='coc_forms')
    op.drop_constraint('fk_coc_forms_unit_id', 'coc_forms', type_='foreignkey')
    op.drop_column('coc_forms', 'unit_id')


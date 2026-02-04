"""create_pricing_plan

Revision ID: 64940eae70c7
Revises: 4b5a6a0f9af0
Create Date: 2026-02-04 17:16:53.626692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64940eae70c7'
down_revision: Union[str, Sequence[str], None] = '4b5a6a0f9af0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_plan_enum = sa.Enum(
        'solo_inspector',
        'enterprise',
        'enterprise_plus',
        name='user_plan_enum',
        create_type=False,
    )
    billing_period_enum = sa.Enum(
        'monthly',
        'yearly',
        name='billing_period_enum',
        create_type=False,
    )
    currency_enum = sa.Enum(
        'USD',
        name='currency_enum',
        create_type=False,
    )

    op.create_table(
        'pricing_plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan', user_plan_enum, nullable=False),
        sa.Column('period', billing_period_enum, nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('currency', currency_enum, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan', 'period', name='uq_pricing_plan_period')
    )

    op.execute(
        """
        INSERT INTO pricing_plans (plan, period, price, currency)
        VALUES
            ('solo_inspector'::user_plan_enum, 'monthly'::billing_period_enum, 50000, 'USD'::currency_enum),
            ('solo_inspector'::user_plan_enum, 'yearly'::billing_period_enum, 500000, 'USD'::currency_enum),
            ('enterprise'::user_plan_enum, 'monthly'::billing_period_enum, 100000, 'USD'::currency_enum),
            ('enterprise'::user_plan_enum, 'yearly'::billing_period_enum, 1000000, 'USD'::currency_enum),
            ('enterprise_plus'::user_plan_enum, 'monthly'::billing_period_enum, 200000, 'USD'::currency_enum),
            ('enterprise_plus'::user_plan_enum, 'yearly'::billing_period_enum, 2000000, 'USD'::currency_enum)
        """
    )


def downgrade() -> None:
    op.drop_table('pricing_plans')

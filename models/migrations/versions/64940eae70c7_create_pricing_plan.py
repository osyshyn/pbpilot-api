from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '64940eae70c7'
down_revision: Union[str, Sequence[str], None] = '4b5a6a0f9af0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_plan_enum = postgresql.ENUM(
        'SOLO_INSPECTOR', 'ENTERPRISE', 'ENTERPRISE_PLUS',
        name='user_plan_enum',
        create_type=False
    )
    billing_period_enum = postgresql.ENUM(
        'MONTHLY', 'YEARLY',
        name='billing_period_enum',
        create_type=False
    )
    currency_enum = postgresql.ENUM(
        'USD',
        name='currency_enum',
        create_type=False
    )

    user_plan_enum.create(op.get_bind(), checkfirst=True)
    billing_period_enum.create(op.get_bind(), checkfirst=True)
    currency_enum.create(op.get_bind(), checkfirst=True)

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
            ('SOLO_INSPECTOR'::user_plan_enum, 'MONTHLY'::billing_period_enum, 50000, 'USD'::currency_enum),
            ('SOLO_INSPECTOR'::user_plan_enum, 'YEARLY'::billing_period_enum, 500000, 'USD'::currency_enum),
            ('ENTERPRISE'::user_plan_enum, 'MONTHLY'::billing_period_enum, 100000, 'USD'::currency_enum),
            ('ENTERPRISE'::user_plan_enum, 'YEARLY'::billing_period_enum, 1000000, 'USD'::currency_enum)
        """
    )


def downgrade() -> None:
    op.drop_table('pricing_plans')

    sa.Enum(name='user_plan_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='billing_period_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='currency_enum').drop(op.get_bind(), checkfirst=True)

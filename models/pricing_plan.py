from enum import StrEnum

from sqlalchemy import Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseIdMixin, BaseTimeStampMixin


class UserPlanEnum(StrEnum):
    """Enumeration of user plans."""

    SOLO_INSPECTOR = 'SOLO_INSPECTOR'
    ENTERPRISE = 'ENTERPRISE'
    ENTERPRISE_PLUS = 'ENTERPRISE_PLUS'


class BillingPeriodEnum(StrEnum):
    """Enumeration of billing periods."""

    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'


class CurrencyEnum(StrEnum):
    """Enumeration of currencies."""

    USD = 'USD'


class PricingPlan(BaseIdMixin, BaseTimeStampMixin):
    __tablename__ = 'pricing_plans'

    plan: Mapped[UserPlanEnum] = mapped_column(
        Enum(UserPlanEnum, name='user_plan_enum', create_type=False),
        nullable=False,
    )
    period: Mapped[BillingPeriodEnum] = mapped_column(
        Enum(BillingPeriodEnum, name='billing_period_enum', create_type=False),
        nullable=False,
    )
    price: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(
        Enum(CurrencyEnum, name='currency_enum', create_type=False),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint('plan', 'period', name='uq_pricing_plan_period'),
    )

    def __repr__(self) -> str:
        return f'<PricingPlan {self.plan} {self.period} {self.price}{self.currency}>'

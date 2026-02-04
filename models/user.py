from enum import StrEnum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete
from models.pricing_plan import UserPlanEnum, BillingPeriodEnum


class UserRoleEnum(StrEnum):
    """Enumeration of user roles."""

    ADMIN = 'admin'
    MANAGER = 'manager'
    INSPECTOR = 'inspector'
    SOLO_OPERATOR = 'solo'


class User(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    """User model represents a system user.

    Fields:
    - name: First name of the user.
    - surname: Last name of the user.
    - email: Unique email for login and contact.
    - password: Hashed password of the user.
    - role: User role (admin or provider).
    - is_active: Indicates if user is active.
    """

    __tablename__ = 'users'

    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment='First name of the user',
    )
    surname: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment='Last name of the user',
    )
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True,
        comment='Unique email address for login',
    )
    password: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        comment='Hashed password',
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(16), nullable=True, comment='Phone number of the user'
    )
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum, name='user_role_enum', create_type=False),
        nullable=False,
        default=UserRoleEnum.SOLO_OPERATOR,
    )
    # Billing settings
    current_plan: Mapped[UserPlanEnum] = mapped_column(
        Enum(UserPlanEnum, name="user_plan_enum"),
        nullable=True,
    )
    billing_period: Mapped[BillingPeriodEnum] = mapped_column(
        Enum(BillingPeriodEnum, name="billing_period_enum"),
        nullable=True,
    )
    free_reports_count: Mapped[int] = mapped_column(
        nullable=True,
        default=0
    )

    def __repr__(self) -> str:
        """Return a string representation of the User object."""
        return f'<User {self.email} ({self.role})>'

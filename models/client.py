from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete


class Client(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'clients'
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment='First name of the client',
    )
    surname: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment='Last name of the client',
    )
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True,
        comment='Unique email address for login',
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(16), nullable=True, comment='Phone number of the user'
    )

    business_address: Mapped[str] = mapped_column(String(255), nullable=False)

    @property
    def full_name(self) -> str:
        """Return the full name of the client."""
        return f'{self.name} {self.surname}'

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete

if TYPE_CHECKING:
    from models.projects import Project


class Client(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'clients'

    __table_args__ = (
        Index(
            'uq_clients_email_not_deleted',
            'email',
            unique=True,
            postgresql_where=text('deleted_at IS NULL'),
        ),
    )

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

    projects: Mapped[list['Project']] = relationship(
        back_populates='client',
        cascade='all, delete-orphan',
    )

    @property
    def full_name(self) -> str:
        """Return the full name of the client."""
        return f'{self.name} {self.surname}'

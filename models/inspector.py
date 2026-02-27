from __future__ import annotations

from datetime import date
from enum import StrEnum

from sqlalchemy import Enum, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete


class LicenseTypeEnum(StrEnum):
    LEAD_CLEARANCE_TECHNICIAN = 'LEAD_CLEARANCE_TECHNICIAN'
    LEAD_INSPECTOR = 'LEAD_INSPECTOR'
    RISK_ASSESSOR = 'RISK_ASSESSOR'
    PROJECT_DESIGNER = 'PROJECT_DESIGNER'


class Inspector(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'inspectors'

    __table_args__ = (
        Index(
            'uq_inspector_email_not_deleted',
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

    license_number: Mapped[str] = mapped_column(
        String(255), comment='License number of the inspector'
    )

    licence_type: Mapped[LicenseTypeEnum] = mapped_column(
        Enum(
            LicenseTypeEnum,
            name='inspector_licence_type_enum',
            create_type=False,
        ),
    )
    issue_date: Mapped[date]
    expiration_date: Mapped[date]

    license_image_keys: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment='S3 keys for license images',
    )

    equipments: Mapped[list['Equipment']] = relationship(
        'Equipment',
        back_populates='inspector',
        cascade='all, delete-orphan',
    )

    @property
    def full_name(self) -> str:
        """Return the full name of the client."""
        return f'{self.name} {self.surname}'

    def __repr__(self) -> str:
        return f'<Inspetor {self.full_name}>'

from __future__ import annotations

from datetime import date
from enum import StrEnum

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete


class OperationModeEnum(StrEnum):
    X_RAY_TUBE = 'X_RAY_TUBE'
    RADIOACTIVE_ISOTOPE = 'RADIOACTIVE_ISOTOPE'


class Equipment(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'equipments'

    inspector_id: Mapped[int] = mapped_column(
        ForeignKey('inspectors.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
    )
    manufacturer: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
    )
    model: Mapped[str] = mapped_column(
        String(254),
    )
    serial_number: Mapped[str] = mapped_column(
        String(254),
    )

    mode: Mapped[OperationModeEnum] = mapped_column(
        Enum(OperationModeEnum, name='operation_mode_enum', create_type=False),
        nullable=False,
    )

    date_of_radioactive_source: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    training_certificate_keys: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment='S3 keys for training certificate images',
    )

    inspector: Mapped['Inspector'] = relationship(
        'Inspector',
        back_populates='equipments',
    )

    def __repr__(self) -> str:
        return f'<Equipment {self.name}>'

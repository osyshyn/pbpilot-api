from datetime import datetime, date
from enum import StrEnum

from sqlalchemy import TIMESTAMP, Index, String, text, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete

class OperationModeEnum(StrEnum):
    X_RAY_TUBE = "X_RAY_TUBE"
    RADIOACTIVE_ISOTOPE = "RADIOACTIVE_ISOTOPE"

class Equipment(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'equipments'

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

    training_certificate_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment='S3 key for image',
    )


    def __repr__(self) -> str:
        return f'<Equipment {self.name}>'


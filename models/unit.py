from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseTimeStampMixin, BaseUUIDMixin

if TYPE_CHECKING:
    from models.jobs import Job
    from models.observation import Observation
    from models.sampling import COCForm


class Unit(BaseUUIDMixin, BaseTimeStampMixin):
    __tablename__ = 'units'

    job_id: Mapped[int] = mapped_column(
        ForeignKey('jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_common_area: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    floor_plan_s3_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    floor_plan_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment='Arbitrary JSON data from Flutter for floor plan construction',
    )

    job: Mapped['Job'] = relationship(back_populates='units')
    rooms: Mapped[list['Room']] = relationship(
        back_populates='unit',
        cascade='all, delete-orphan',
    )
    coc_forms: Mapped[list['COCForm']] = relationship(
        back_populates='unit',
        cascade='all, delete-orphan',
    )


class Room(BaseUUIDMixin, BaseTimeStampMixin):
    __tablename__ = 'rooms'

    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('units.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    unit: Mapped['Unit'] = relationship(back_populates='rooms')
    observations: Mapped[list['Observation']] = relationship(
        back_populates='room',
        cascade='all, delete-orphan',
    )


from __future__ import annotations

import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseTimeStampMixin, BaseUUIDMixin

if TYPE_CHECKING:
    from models.jobs import Job
    from models.unit import Room


class ObservationCategoryEnum(StrEnum):
    """Enumeration of observation categories.

    INFO is used for general/title-page photos (e.g. in PDF report generation)
    and can be filtered separately from hazard/future-risk/exclusion observations.
    """

    HAZARD = 'HAZARD'
    FUTURE_RISK = 'FUTURE_RISK'
    EXCLUSION = 'EXCLUSION'
    INFO = 'INFO'


class Observation(BaseUUIDMixin, BaseTimeStampMixin):
    __tablename__ = 'observations'

    job_id: Mapped[int] = mapped_column(
        ForeignKey('jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('rooms.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    category: Mapped[ObservationCategoryEnum] = mapped_column(
        Enum(
            ObservationCategoryEnum,
            name='observation_category_enum',
            create_type=False,
        ),
        nullable=False,
    )
    is_exterior: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    component: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    side: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    condition: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    identifiers: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    raw_text: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )

    job: Mapped['Job'] = relationship(back_populates='observations')
    room: Mapped['Room | None'] = relationship(back_populates='observations')
    photos: Mapped[list['Photo']] = relationship(
        back_populates='observation',
        cascade='all, delete-orphan',
    )


class Photo(BaseUUIDMixin, BaseTimeStampMixin):
    __tablename__ = 'photos'

    observation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('observations.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    s3_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    descriptions: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        comment='Optional descriptions/caption for the photo',
    )

    observation: Mapped['Observation'] = relationship(back_populates='photos')


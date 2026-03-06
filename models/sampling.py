from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseTimeStampMixin, BaseUUIDMixin
from models.jobs import SampleTypeEnum

if TYPE_CHECKING:
    from models.jobs import Job
    from models.unit import Unit


class COCForm(BaseUUIDMixin, BaseTimeStampMixin):
    __tablename__ = 'coc_forms'

    job_id: Mapped[int] = mapped_column(
        ForeignKey('jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('units.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )

    job: Mapped['Job'] = relationship(back_populates='coc_forms')
    unit: Mapped['Unit | None'] = relationship(back_populates='coc_forms')
    samples: Mapped[list['Sample']] = relationship(
        back_populates='coc_form',
        cascade='all, delete-orphan',
    )


class SamplePhoto(BaseUUIDMixin, BaseTimeStampMixin):
    """Photo of sampling location; a sample can have multiple photos."""

    __tablename__ = 'sample_photos'

    sample_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('samples.id', ondelete='CASCADE'),
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

    sample: Mapped['Sample'] = relationship(back_populates='photos')


class Sample(BaseUUIDMixin, BaseTimeStampMixin):
    __tablename__ = 'samples'

    coc_form_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('coc_forms.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    sample_type: Mapped[SampleTypeEnum] = mapped_column(
        Enum(
            SampleTypeEnum,
            name='sample_type_enum',
            create_type=False,
        ),
        nullable=False,
    )
    barcode_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='Short sample barcode like "01", "02".',
    )
    location_description: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    side: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    component: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    soil_area: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    photo_s3_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment='Deprecated: use sample_photos relation. Kept for backward compatibility.',
    )

    coc_form: Mapped['COCForm'] = relationship(back_populates='samples')
    photos: Mapped[list['SamplePhoto']] = relationship(
        back_populates='sample',
        cascade='all, delete-orphan',
    )


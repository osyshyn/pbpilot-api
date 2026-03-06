from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete
from models import Inspector

if TYPE_CHECKING:
    from models.job_auxiliary import JobDocument
    from models.observation import Observation
    from models.projects import ProjectProperty
    from models.sampling import COCForm
    from models.unit import Unit


class InspectionTypeEnum(StrEnum):
    PERSONAL_BUSINESS_METING = 'PERSONAL_BUSINESS_METING'
    CONSULTATION = 'CONSULTATION'
    RISK_ASSESSMENT = 'RISK_ASSESSMENT'
    LIRA = 'LIRA'
    CLEARANCE = 'CLEARANCE'
    PRE_INSPECTION = 'PRE_INSPECTION'
    SAMPLING = 'SAMPLING'
    RETEST = 'RETEST'


class JobStatusEnum(StrEnum):
    COMPLETED = 'COMPLETED'
    IN_PROGRESS = 'IN_PROGRESS'
    SCHEDULED = 'SCHEDULED'
    AWAITING_RESULTS = 'AWAITING_RESULTS'


class SampleTypeEnum(StrEnum):
    PAINT_CHIP = 'PAINT_CHIP'
    DUST_WIPE = 'DUST_WIPE'
    WATER = 'WATER'
    SOIL = 'SOIL'


class Job(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'jobs'

    __table_args__ = (
        Index(
            'ix_jobs_property_not_deleted',
            'property_id',
            postgresql_where=text('deleted_at IS NULL'),
        ),
        Index(
            'ix_jobs_inspector_not_deleted',
            'inspector_id',
            postgresql_where=text('deleted_at IS NULL'),
        ),
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey('project_properties.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    inspector_id: Mapped[int | None] = mapped_column(
        ForeignKey('inspectors.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )

    parent_job_id: Mapped[int | None] = mapped_column(
        ForeignKey('jobs.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment='Original job for RETEST inspections',
    )

    inspection_type: Mapped[InspectionTypeEnum] = mapped_column(
        Enum(
            InspectionTypeEnum,
            name='inspection_type_enum',
            create_type=False,
        ),
        nullable=False,
    )
    status: Mapped[JobStatusEnum] = mapped_column(
        Enum(JobStatusEnum, name='job_status_enum', create_type=False),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    property: Mapped['ProjectProperty'] = relationship(back_populates='jobs')
    inspector: Mapped[Inspector | None] = relationship()
    parent_job: Mapped['Job | None'] = relationship(
        'Job',
        remote_side='Job.id',
        back_populates='retest_jobs',
    )
    retest_jobs: Mapped[list['Job']] = relationship(
        'Job',
        back_populates='parent_job',
        cascade='all, delete-orphan',
    )
    observations: Mapped[list['Observation']] = relationship(
        back_populates='job',
        cascade='all, delete-orphan',
    )
    units: Mapped[list['Unit']] = relationship(
        back_populates='job',
        cascade='all, delete-orphan',
    )
    coc_forms: Mapped[list['COCForm']] = relationship(
        back_populates='job',
        cascade='all, delete-orphan',
    )
    exterior_observations: Mapped[list['Observation']] = relationship(
        primaryjoin=(
            'and_(Observation.job_id == Job.id, '
            'Observation.is_exterior == True)'
        ),
        viewonly=True,
    )
    documents: Mapped[list['JobDocument']] = relationship(
        back_populates='job',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'<Job id={self.id} type={self.inspection_type}>'

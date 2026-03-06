"""Auxiliary job-related models: documents."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseTimeStampMixin, BaseUUIDMixin

if TYPE_CHECKING:
    from models.jobs import Job


class JobDocument(BaseUUIDMixin, BaseTimeStampMixin):
    """Stores PDF/DOCX files attached to an inspection (e.g. Clearance).

    Examples: lead hazard control orders, legacy reports, estimates.
    """

    __tablename__ = 'job_documents'

    job_id: Mapped[int] = mapped_column(
        ForeignKey('jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    s3_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    job: Mapped['Job'] = relationship(back_populates='documents')

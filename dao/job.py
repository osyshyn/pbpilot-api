from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import cast, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.types import Date

from core.dao import BaseDAO
from models import COCForm, Job, JobDocument, Observation, Photo, Project, ProjectProperty, Room, Sample, Unit
from models.jobs import JobStatusEnum


class JobDAO(BaseDAO):
    """DAO for Job model with hierarchical access helpers."""

    async def create(
        self,
        *,
        property_id: int,
        inspector_id: int | None,
        inspection_type: str,
        notes: str | None,
        status: JobStatusEnum = JobStatusEnum.SCHEDULED,
    ) -> Job:
        job = Job(
            property_id=property_id,
            inspector_id=inspector_id,
            inspection_type=inspection_type,
             status=status,
            notes=notes,
        )
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def get_by_id(self, job_id: int) -> Job | None:
        stmt = select(Job).where(
            Job.id == job_id,
            Job.is_active == True,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_by_id(
        self,
        job_id: int,
        update_data: dict[str, Any],
    ) -> Job | None:
        """Update job by id."""
        job = await self.get_by_id(job_id)
        if not job:
            return None
        for key, value in update_data.items():
            if hasattr(job, key):
                setattr(job, key, value)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def get_by_id_with_relations(self, job_id: int) -> Job | None:
        """Get job with basic property and inspector relations."""
        stmt = (
            select(Job)
            .where(
                Job.id == job_id,
                Job.is_active == True,  # noqa: E712
            )
            .options(
                selectinload(Job.property)
                .selectinload(ProjectProperty.project)
                .selectinload(Project.client),
                selectinload(Job.inspector),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_job_with_full_hierarchy(self, job_id: int) -> Job | None:
        """Get job with full hierarchy for PDF/mobile consumption.

        Loads:
        - property → project → client
        - inspector
        - units → rooms → observations → photos
        - exterior observations → photos
        - job-level and unit-level COC forms → samples
        - documents and calendar events
        """
        stmt = (
            select(Job)
            .where(
                Job.id == job_id,
                Job.is_active == True,
            )
            .options(
                selectinload(Job.property)
                .selectinload(ProjectProperty.project)
                .selectinload(Project.client),
                selectinload(Job.inspector),
                selectinload(Job.documents).selectinload(JobDocument.job),
                selectinload(Job.units)
                .selectinload(Unit.rooms)
                .selectinload(Room.observations)
                .selectinload(Observation.photos),
                selectinload(Job.exterior_observations).selectinload(
                    Observation.photos,
                ),
                selectinload(Job.coc_forms)
                .selectinload(COCForm.samples)
                .selectinload(Sample.coc_form),
                selectinload(Job.units)
                .selectinload(Unit.coc_forms)
                .selectinload(COCForm.samples),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_retest_history(self, parent_job_id: int) -> list[Job]:
        """Get all re-test jobs for the original inspection."""
        stmt = (
            select(Job)
            .where(
                Job.parent_job_id == parent_job_id,
                Job.is_active == True,
            )
            .order_by(Job.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(
        self,
        page: int,
        limit: int,
    ) -> tuple[list[Job], int]:
        stmt = select(Job).where(Job.is_active == True)  # noqa: E712
        return await self.paginate(query=stmt, page=page, limit=limit)

    async def get_all_by_property_id(self, property_id: int) -> list[Job]:
        stmt = select(Job).where(
            Job.property_id == property_id,
            Job.is_active == True,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_by_inspector_id(self, inspector_id: int) -> list[Job]:
        stmt = select(Job).where(
            Job.inspector_id == inspector_id,
            Job.is_active == True,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_project_id(
        self,
        project_id: int,
        page: int,
        limit: int,
        *,
        status: JobStatusEnum | None = None,
        inspector_id: int | None = None,
        created_on_date: date | None = None,
    ) -> tuple[list[Job], int]:
        stmt = (
            select(Job)
            .join(ProjectProperty, Job.property_id == ProjectProperty.id)
            .where(
                ProjectProperty.project_id == project_id,
                Job.is_active == True,  # noqa: E712
            )
            .options(
                selectinload(Job.property).selectinload(
                    ProjectProperty.project,
                ),
                selectinload(Job.inspector),
            )
        )
        if status is not None:
            stmt = stmt.where(Job.status == status)
        if inspector_id is not None:
            stmt = stmt.where(Job.inspector_id == inspector_id)
        if created_on_date is not None:
            stmt = stmt.where(cast(Job.created_at, Date) == created_on_date)
        return await self.paginate(query=stmt, page=page, limit=limit)

    async def get_by_inspector_id_paginated(
        self,
        inspector_id: int,
        page: int,
        limit: int,
    ) -> tuple[list[Job], int]:
        stmt = (
            select(Job)
            .where(
                Job.inspector_id == inspector_id,
                Job.is_active == True,  # noqa: E712
            )
            .options(
                selectinload(Job.property).selectinload(
                    ProjectProperty.project,
                ),
                selectinload(Job.inspector),
            )
        )
        return await self.paginate(query=stmt, page=page, limit=limit)

    async def delete_by_id(self, job_id: int) -> Job | None:
        stmt = (
            update(Job)
            .where(Job.id == job_id, Job.is_active == True)  # noqa: E712
            .values(is_active=False, deleted_at=datetime.now(UTC))
            .returning(Job)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

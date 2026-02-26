from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from core.dao import BaseDAO
from models import Job, Project, ProjectProperty


class JobDAO(BaseDAO):
    """DAO for Job model."""

    async def create(
        self,
        *,
        property_id: int,
        inspector_id: int | None,
        inspection_type: str,
        notes: str | None,
    ) -> Job:
        job = Job(
            property_id=property_id,
            inspector_id=inspector_id,
            inspection_type=inspection_type,
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
                    ProjectProperty.project
                ),
                selectinload(Job.inspector),
            )
        )
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
                    ProjectProperty.project
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

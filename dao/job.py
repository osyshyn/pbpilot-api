from sqlalchemy import select

from core.dao import BaseDAO
from models import Job


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


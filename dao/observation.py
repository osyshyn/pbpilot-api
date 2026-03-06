from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select

from core.dao import BaseDAO
from models import Observation, Photo


class ObservationDAO(BaseDAO):
    """DAO for Observation model."""

    async def bulk_create(
        self,
        *,
        observations_data: list[dict[str, Any]],
    ) -> list[Observation]:
        """Bulk insert observations for offline/mobile sync."""
        if not observations_data:
            return []
        observations = [Observation(**data) for data in observations_data]
        self._session.add_all(observations)
        await self._session.flush()
        return observations

    async def get_by_job_id(self, job_id: int) -> list[Observation]:
        stmt = select(Observation).where(Observation.job_id == job_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_exterior_by_job_id(self, job_id: int) -> None:
        """Delete all exterior observations for a job."""
        stmt = delete(Observation).where(
            Observation.job_id == job_id,
            Observation.is_exterior == True,
        )
        await self._session.execute(stmt)


class PhotoDAO(BaseDAO):
    """DAO for Photo model."""

    async def bulk_create(
        self,
        *,
        photos_data: list[dict[str, Any]],
    ) -> list[Photo]:
        """Bulk insert photos linked to observations."""
        if not photos_data:
            return []
        photos = [Photo(**data) for data in photos_data]
        self._session.add_all(photos)
        await self._session.flush()
        return photos


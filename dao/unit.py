from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select

from core.dao import BaseDAO
from models import Room, Unit


class UnitDAO(BaseDAO):
    """DAO for Unit model."""

    async def create(
        self,
        *,
        job_id: int,
        name: str,
        is_common_area: bool,
        floor_plan_s3_key: str | None = None,
        floor_plan_data: dict[str, Any] | None = None,
    ) -> Unit:
        unit = Unit(
            job_id=job_id,
            name=name,
            is_common_area=is_common_area,
            floor_plan_s3_key=floor_plan_s3_key,
            floor_plan_data=floor_plan_data,
        )
        self._session.add(unit)
        await self._session.flush()
        await self._session.refresh(unit)
        return unit

    async def bulk_create(
        self,
        *,
        units_data: list[dict[str, Any]],
    ) -> list[Unit]:
        """Efficient bulk insert for units (used in offline sync)."""
        if not units_data:
            return []
        units = [Unit(**data) for data in units_data]
        self._session.add_all(units)
        await self._session.flush()
        return units

    async def get_by_job_id(self, job_id: int) -> list[Unit]:
        stmt = select(Unit).where(Unit.job_id == job_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_job_id(self, job_id: int) -> None:
        """Delete all units for a job (cascades to rooms and children)."""
        stmt = delete(Unit).where(Unit.job_id == job_id)
        await self._session.execute(stmt)


class RoomDAO(BaseDAO):
    """DAO for Room model."""

    async def bulk_create(
        self,
        *,
        rooms_data: list[dict[str, Any]],
    ) -> list[Room]:
        """Efficient bulk insert for rooms."""
        if not rooms_data:
            return []
        rooms = [Room(**data) for data in rooms_data]
        self._session.add_all(rooms)
        await self._session.flush()
        return rooms


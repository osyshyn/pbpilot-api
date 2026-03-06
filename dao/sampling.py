from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from core.dao import BaseDAO
from models import COCForm, Sample, SamplePhoto


class COCFormDAO(BaseDAO):
    """DAO for COCForm model."""

    async def get_active_forms_for_job(self, job_id: int) -> list[COCForm]:
        """Return only active forms for a given job."""
        stmt = (
            select(COCForm)
            .where(
                COCForm.job_id == job_id,
                COCForm.is_active == True,
            )
            .options(selectinload(COCForm.samples))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def archive_existing_forms(self, job_id: int) -> None:
        """Mark all existing forms for job as inactive."""
        stmt = (
            update(COCForm)
            .where(COCForm.job_id == job_id)
            .values(is_active=False)
        )
        await self._session.execute(stmt)

    async def bulk_create(
        self,
        *,
        forms_data: list[dict[str, Any]],
    ) -> list[COCForm]:
        """Bulk insert COC forms."""
        if not forms_data:
            return []
        forms = [COCForm(**data) for data in forms_data]
        self._session.add_all(forms)
        await self._session.flush()
        return forms

    async def delete_by_job_id(self, job_id: int) -> None:
        """Delete all COC forms (and samples via cascade) for a job."""
        stmt = delete(COCForm).where(COCForm.job_id == job_id)
        await self._session.execute(stmt)


class SampleDAO(BaseDAO):
    """DAO for Sample model."""

    async def bulk_create(
        self,
        *,
        samples_data: list[dict[str, Any]],
    ) -> list[Sample]:
        """Bulk insert lab samples."""
        if not samples_data:
            return []
        samples = [Sample(**data) for data in samples_data]
        self._session.add_all(samples)
        await self._session.flush()
        return samples


class SamplePhotoDAO(BaseDAO):
    """DAO for SamplePhoto model."""

    async def bulk_create(
        self,
        *,
        sample_photos_data: list[dict[str, Any]],
    ) -> list[SamplePhoto]:
        """Bulk insert photos linked to samples."""
        if not sample_photos_data:
            return []
        photos = [SamplePhoto(**data) for data in sample_photos_data]
        self._session.add_all(photos)
        await self._session.flush()
        return photos


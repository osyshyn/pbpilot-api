from __future__ import annotations

from typing import Any

from sqlalchemy import select

from core.dao import BaseDAO
from models import JobDocument


class JobDocumentDAO(BaseDAO):
    """DAO for JobDocument model."""

    async def bulk_create(
        self,
        *,
        documents_data: list[dict[str, Any]],
    ) -> list[JobDocument]:
        """Bulk insert job documents (e.g. clearance letters)."""
        if not documents_data:
            return []
        documents = [JobDocument(**data) for data in documents_data]
        self._session.add_all(documents)
        await self._session.flush()
        return documents

    async def get_by_job_id(self, job_id: int) -> list[JobDocument]:
        stmt = select(JobDocument).where(JobDocument.job_id == job_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import InspectorDAO, JobDAO
from exceptions import JobNotFoundException, ProjectPropertyNotFoundException
from exceptions.user import UserNotFoundByIdException
from models import Job
from models.projects import ProjectProperty
from schemas import CreateJobRequestSchema

logger = logging.getLogger(__name__)


class JobService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        job_dao: JobDAO | None = None,
        inspector_dao: InspectorDAO | None = None,
    ):
        super().__init__(db_session)
        self._job_dao = job_dao or JobDAO(db_session)
        self._inspector_dao = inspector_dao or InspectorDAO(db_session)

    async def create_job(self, data: CreateJobRequestSchema) -> Job:
        property_stmt = select(ProjectProperty).where(
            ProjectProperty.id == data.property_id,
            ProjectProperty.is_active == True,  # noqa: E712
        )
        result = await self._session.execute(property_stmt)
        project_property = result.scalar_one_or_none()
        if not project_property:
            raise ProjectPropertyNotFoundException

        if data.inspector_id is not None:
            inspector = await self._inspector_dao.get_by_id(data.inspector_id)
            if not inspector or not inspector.is_active:
                raise UserNotFoundByIdException

        job = await self._job_dao.create(
            property_id=data.property_id,
            inspector_id=data.inspector_id,
            inspection_type=data.inspection_type.value,
            notes=data.notes,
        )
        await self._session.commit()
        return job

    async def get_job_by_id(self, job_id: int) -> Job:
        job = await self._job_dao.get_by_id(job_id)
        if not job:
            raise JobNotFoundException
        return job

    async def delete_job_by_id(self, job_id: int) -> Job:
        job = await self._job_dao.delete_by_id(job_id)
        if not job:
            raise JobNotFoundException
        await self._session.commit()
        return job

    async def get_all_jobs(
        self,
        pagination: PaginationParams,
    ) -> tuple[list[Job], int]:
        return await self._job_dao.get_all(
            page=pagination.page,
            limit=pagination.size,
        )


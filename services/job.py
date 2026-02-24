import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import InspectorDAO, JobDAO, ProjectDAO
from exceptions import ProjectNotFoundException
from exceptions.user import UserNotFoundByIdException
from models import Job
from schemas import CreateJobRequestSchema

logger = logging.getLogger(__name__)


class JobService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        job_dao: JobDAO | None = None,
        project_dao: ProjectDAO | None = None,
        inspector_dao: InspectorDAO | None = None,
    ):
        super().__init__(db_session)
        self._job_dao = job_dao or JobDAO(db_session)
        self._project_dao = project_dao or ProjectDAO(db_session)
        self._inspector_dao = inspector_dao or InspectorDAO(db_session)

    async def create_job(self, data: CreateJobRequestSchema) -> Job:

        project = await self._project_dao.get_by_id_with_relations(
            data.property_id
        )
        if not project:
            raise ProjectNotFoundException

        if data.inspector_id is not None:
            inspector = await self._inspector_dao.get_by_id(data.inspector_id)
            if not inspector or not inspector.is_active:
                raise UserNotFoundByIdException

        job = await self._job_dao.create(
            property_id=data.property_id, #TODO: Move it for DTO
            inspector_id=data.inspector_id,
            inspection_type=data.inspection_type.value,
            notes=data.notes,
        )
        await self._session.commit()
        return job


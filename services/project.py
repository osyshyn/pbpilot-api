import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import ClientDAO, ProjectDAO
from exceptions import ClientNotFoundException
from models import Project
from schemas.projects import CreateProjectRequestSchema

logger = logging.getLogger(__name__)


class ProjectService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        project_dao: ProjectDAO | None = None,
        client_dao: ClientDAO | None = None,
    ):
        super().__init__(db_session)
        self._project_dao = project_dao or ProjectDAO(db_session)
        self._client_dao = client_dao or ClientDAO(db_session)

    async def create_project(self, data: CreateProjectRequestSchema) -> Project:
        """Create a project with properties and structures."""
        client = await self._client_dao.get_by_id(data.client_id)
        if not client:
            raise ClientNotFoundException
        project = await self._project_dao.create_with_properties(
            client_id=data.client_id,
            project_name=data.project_name,
            property_manager_name=data.property_manager,
            properties_data=data.properties,
        )
        await self._session.commit()
        project = await self._project_dao.get_by_id_with_relations(project.id)
        if not project:
            raise RuntimeError('Project was not found after create')
        return project

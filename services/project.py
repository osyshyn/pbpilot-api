import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import ClientDAO, ProjectDAO
from exceptions import ClientNotFoundException, ProjectNotFoundException
from models import Project
from schemas.projects import CreateProjectRequestSchema
from dto import OngoingProjectDTO, NeedScheduledDTO, UnassignedJobsDTO, \
    ReadyToFinalizeDTO, ProjectDashboardDTO

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
        created_project = await self._project_dao.create_with_properties(
            client_id=data.client_id,
            project_name=data.project_name,
            property_manager_name=data.property_manager,
            properties_data=data.properties,
        )
        await self._session.commit()
        project = await self._project_dao.get_by_id_with_relations(
            created_project.id
        )
        if not project:
            raise ProjectNotFoundException
        return project

    async def get_project_by_id(self, project_id: int) -> Project:
        """Get single project with its properties and structures."""
        project = await self._project_dao.get_by_id_with_relations(project_id)
        if not project:
            raise ProjectNotFoundException
        return project

    async def delete_by_id(self, project_id: int) -> Project:
        """Soft delete project by id."""
        project = await self._project_dao.delete_by_id(project_id)
        if not project:
            raise ProjectNotFoundException
        await self._session.commit()
        return project

    async def get_all_projects(
        self,
        page: int,
        size: int,
    ) -> tuple[list[Project], int]:
        """Get all active projects with pagination."""
        return await self._project_dao.get_all(page=page, limit=size)

    async def get_projects_dashboard(
            self
    ) -> ProjectDashboardDTO:
        return await self._project_dao.get_projects_dashboard()

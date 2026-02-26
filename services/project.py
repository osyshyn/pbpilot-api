import logging
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import ClientDAO, ProjectDAO
from dto import (
    ProjectDashboardDTO,
)
from exceptions import (
    ClientEmailAlreadyRegisteredException,
    ClientNotFoundException,
    ProjectNotFoundException,
)
from models import Project
from models.projects import ProjectStatusEnum
from schemas.projects import (
    CreateProjectRequestSchema,
    UpdateProjectRequestSchema,
)

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

    async def search_by_name(self, project_name: str) -> list[Project]:
        return await self._project_dao.search_by_name(
            project_name=project_name,
        )

    async def create_project(self, data: CreateProjectRequestSchema) -> Project:
        """Create a project with properties and structures."""
        client = await self._client_dao.get_by_id(data.client_id)
        if not client:
            raise ClientNotFoundException
        await self._client_dao.update_last_activity(client_id=client.id)
        created_project = await self._project_dao.create_with_properties(
            client_id=data.client_id,
            project_name=data.project_name,
            property_manager_name=data.property_manager,
            properties_data=data.properties,
            status=ProjectStatusEnum.IN_PROGRESS,
        )
        await self._session.commit()
        project = await self._project_dao.get_by_id_with_relations(
            created_project.id
        )
        if not project:
            raise ProjectNotFoundException
        return project

    async def update_project(
        self,
        project_id: int,
        project_update_data: UpdateProjectRequestSchema,
    ) -> Project:
        """Update project name and related contact data."""
        update_data = project_update_data.model_dump(exclude_unset=True)

        project_update_fields: dict[str, Any] = {}
        client_update_fields: dict[str, Any] = {}

        if 'project_name' in update_data:
            project_update_fields['project_name'] = update_data.pop(
                'project_name'
            )

        if 'email' in update_data:
            client_update_fields['email'] = update_data.pop('email')
        if 'phone_number' in update_data:
            client_update_fields['phone_number'] = update_data.pop(
                'phone_number'
            )

        project = None
        if project_update_fields:
            project = await self._project_dao.update_by_id(
                project_id=project_id,
                update_data=project_update_fields,
            )
            if not project:
                raise ProjectNotFoundException
        else:
            project = await self._project_dao.get_by_id_with_relations(
                project_id
            )
            if not project:
                raise ProjectNotFoundException

        if client_update_fields:
            try:
                client = await self._client_dao.update_by_id(
                    client_id=project.client_id,
                    update_data=client_update_fields,
                )
            except IntegrityError:
                raise ClientEmailAlreadyRegisteredException from None
            if not client:
                raise ClientNotFoundException

        await self._session.commit()
        updated_project = await self._project_dao.get_by_id_with_relations(
            project_id
        )
        if not updated_project:
            raise ProjectNotFoundException
        return updated_project

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

    async def get_projects_dashboard(self, user_id: int) -> ProjectDashboardDTO:
        return await self._project_dao.get_projects_dashboard(user_id=user_id)

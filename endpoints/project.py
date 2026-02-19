import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_admin_user_from_token
from models import User
from schemas.projects import (
    CreateProjectRequestSchema,
    ProjectDashboardResponseSchema,
    ProjectResponseSchema,
)
from services.project import ProjectService

logger = logging.getLogger(__name__)

project_router = APIRouter()


@project_router.get(
    path='/search',
    description='Search projects by name',
)
async def search_projects(
        admin_user: Annotated[User, Depends(get_admin_user_from_token)],
        project_service: Annotated[
            ProjectService, Depends(get_service(ProjectService))
        ],
        project_name: str = Query(
            description='Project name for search',
            examples=['test project'],
        ),
) -> list[ProjectResponseSchema]:
    return [
        ProjectResponseSchema.model_validate(project)
        for project in await project_service.search_by_name(project_name)
    ]


@project_router.get(
    path='/dashboard',
    summary='Get dashboard data',
)
async def get_project_dashboard(
        admin_user: Annotated[User, Depends(get_admin_user_from_token)],
        project_service: Annotated[
            ProjectService, Depends(get_service(ProjectService))
        ],
) -> ProjectDashboardResponseSchema:
    dashboard_dto = await project_service.get_projects_dashboard(admin_user.id)
    return ProjectDashboardResponseSchema.model_validate(dashboard_dto)


@project_router.post(
    path='/',
    summary='Create project',
    dependencies=[Depends(get_admin_user_from_token)],
)
async def create_project(
        project_data: CreateProjectRequestSchema,
        project_service: Annotated[
            ProjectService, Depends(get_service(ProjectService))
        ],
) -> ProjectResponseSchema:
    project = await project_service.create_project(data=project_data)
    return ProjectResponseSchema.model_validate(project)


@project_router.get(
    path='/{project_id}',
    summary='Get project by id',
    dependencies=[Depends(get_admin_user_from_token)],
)
async def get_project_by_id(
        project_id: int,
        project_service: Annotated[
            ProjectService, Depends(get_service(ProjectService))
        ],
) -> ProjectResponseSchema:
    project = await project_service.get_project_by_id(project_id=project_id)
    return ProjectResponseSchema.model_validate(project)


@project_router.delete(
    path='/{project_id}',
    summary='Delete project by id',
    dependencies=[Depends(get_admin_user_from_token)],
)
async def delete_project_by_id(
        project_id: int,
        project_service: Annotated[
            ProjectService, Depends(get_service(ProjectService))
        ],
) -> ProjectResponseSchema:
    project = await project_service.delete_by_id(project_id=project_id)
    return ProjectResponseSchema.model_validate(project)


@project_router.get(
    path='/',
    summary='Get projects list',
    dependencies=[Depends(get_admin_user_from_token)],
)
async def get_all_projects(
        pagination: Annotated[PaginationParams, Depends()],
        project_service: Annotated[
            ProjectService, Depends(get_service(ProjectService))
        ],
) -> PaginatedResponse[ProjectResponseSchema]:
    items, total = await project_service.get_all_projects(
        page=pagination.page,
        size=pagination.size,
    )
    pages = (total + pagination.size - 1) // pagination.size
    return PaginatedResponse(
        items=items,  # type: ignore[arg-type]
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )

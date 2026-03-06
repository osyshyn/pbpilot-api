import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from models import User
from schemas.projects import (
    CreateProjectRequestSchema,
    ProjectDashboardResponseSchema,
    ProjectDetailsResponseSchema,
    ProjectFilesResponseSchema,
    ProjectFiltersSchema,
    ProjectResponseSchema,
    UpdateProjectRequestSchema,
)
from services.project import ProjectService

logger = logging.getLogger(__name__)

project_router = APIRouter()


@project_router.get(
    path='/search',
    description='Search projects by name',
)
async def search_projects(
    admin_user: Annotated[User, Depends(get_current_user)],
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
    admin_user: Annotated[User, Depends(get_current_user)],
    project_service: Annotated[
        ProjectService, Depends(get_service(ProjectService))
    ],
) -> ProjectDashboardResponseSchema:
    dashboard_dto = await project_service.get_projects_dashboard(admin_user.id)
    return ProjectDashboardResponseSchema.model_validate(dashboard_dto)


@project_router.post(
    path='/',
    summary='Create project',
    dependencies=[Depends(get_current_user)],
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
    dependencies=[Depends(get_current_user)],
)
async def get_project_by_id(
    project_id: int,
    project_service: Annotated[
        ProjectService, Depends(get_service(ProjectService))
    ],
) -> ProjectDetailsResponseSchema:
    return ProjectDetailsResponseSchema.model_validate(
        await project_service.get_project_by_id(project_id=project_id)
    )


@project_router.delete(
    path='/{project_id}',
    summary='Delete project by id',
    dependencies=[Depends(get_current_user)],
)
async def delete_project_by_id(
    project_id: int,
    project_service: Annotated[
        ProjectService, Depends(get_service(ProjectService))
    ],
) -> ProjectResponseSchema:
    project = await project_service.delete_by_id(project_id=project_id)
    return ProjectResponseSchema.model_validate(project)


@project_router.patch(
    path='/{project_id}',
    summary='Update project',
    dependencies=[Depends(get_current_user)],
)
async def update_project(
    project_id: int,
    project_update_data: UpdateProjectRequestSchema,
    project_service: Annotated[
        ProjectService, Depends(get_service(ProjectService))
    ],
) -> ProjectResponseSchema:
    project = await project_service.update_project(
        project_id=project_id,
        project_update_data=project_update_data,
    )
    return ProjectResponseSchema.model_validate(project)


@project_router.get(
    path='/',
    summary='Get projects list',
    dependencies=[Depends(get_current_user)],
)
async def get_all_projects(
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[ProjectFiltersSchema, Depends()],
    project_service: Annotated[
        ProjectService, Depends(get_service(ProjectService))
    ],
) -> PaginatedResponse[ProjectResponseSchema]:
    items, total = await project_service.get_all_projects(
        page=pagination.page,
        size=pagination.size,
        status=filters.status,
        client_id=filters.client_id,
        inspector_id=filters.inspector_id,
        date=filters.date,
    )
    pages = (total + pagination.size - 1) // pagination.size
    return PaginatedResponse(
        items=items,  # type: ignore[arg-type]
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )


@project_router.get(
    path='/{project_id}/files',
    summary='Get project files (download links)',
    description=(
        'Returns a list of files associated with the project. '
        'Each file includes an S3 pre-signed URL for direct download. '
        'Currently returns an empty list (stub — S3 integration pending).'
    ),
    dependencies=[Depends(get_current_user)],
)
async def get_project_files(
    project_id: int,
    project_service: Annotated[
        ProjectService, Depends(get_service(ProjectService))
    ],
) -> ProjectFilesResponseSchema:
    return await project_service.get_project_files(project_id=project_id)

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_admin_user_from_token
from schemas.projects import CreateProjectRequestSchema, ProjectResponseSchema
from services.project import ProjectService

logger = logging.getLogger(__name__)

project_router = APIRouter()


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

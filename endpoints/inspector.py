import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from core import get_service
from core.constants import INSPECTOR_LICENSE_PREFIX
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from dto import UploadFileDTO
from models import User
from schemas import (
    CreateInspectorRequestSchema,
    InspectorDashboardResponseSchema,
    InspectorResponseSchema,
    UpdateInspectorRequestSchema,
)
from services import InspectorService
from services.aws import FileUploadService

logger = logging.getLogger(__name__)

inspector_router = APIRouter()


@inspector_router.get(
    path='/',
    summary='Get all inspectors',
    dependencies=[Depends(get_current_user)],
)
async def get_all_inspectors(
    pagination: Annotated[PaginationParams, Depends()],
    inspector_service: Annotated[
        InspectorService, Depends(get_service(InspectorService))
    ],
) -> PaginatedResponse[InspectorResponseSchema]:
    items, total = await inspector_service.get_all_inspectors(
        pagination=pagination
    )
    pages = (total + pagination.size - 1) // pagination.size
    return PaginatedResponse(
        items=items,  # type: ignore
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )


@inspector_router.post(
    path='/',
    summary='Create a new inspector',
    dependencies=[Depends(get_current_user)],
)
async def create_inspector(
    inspector_data: Annotated[
        CreateInspectorRequestSchema,
        Depends(CreateInspectorRequestSchema.from_form),
    ],
    files: Annotated[UploadFile, File()],
    inspector_service: Annotated[
        InspectorService, Depends(get_service(InspectorService))
    ],
    upload_file_service: FileUploadService = Depends(FileUploadService),
) -> InspectorResponseSchema:
    uploaded_files: list[
        UploadFileDTO
    ] = await upload_file_service.upload_files(
        files=files, prefix=INSPECTOR_LICENSE_PREFIX
    )
    return InspectorResponseSchema.model_validate(
        await inspector_service.create_new_inspector(
            inspector_schema=inspector_data,
            license_files=uploaded_files,
        )
    )


@inspector_router.get(
    path='/dashboard',
    summary='Get inspector dashboard data',
    dependencies=[Depends(get_current_user)],
)
async def get_inspector_dashboard(
    admin_user: Annotated[User, Depends(get_current_user)],
    inspector_service: Annotated[
        InspectorService, Depends(get_service(InspectorService))
    ],
) -> InspectorDashboardResponseSchema:
    dashboard_dto = await inspector_service.get_inspectors_dashboard(
        admin_user.id
    )
    return InspectorDashboardResponseSchema.model_validate(dashboard_dto)


@inspector_router.get(
    path='/{inspector_id}',
    summary='Get inspector by id',
    dependencies=[Depends(get_current_user)],
)
async def get_company_by_id(
    inspector_id: int,
    inspector_service: Annotated[
        InspectorService, Depends(get_service(InspectorService))
    ],
) -> InspectorResponseSchema:
    return InspectorResponseSchema.model_validate(
        await inspector_service.get_inspector_by_id(inspector_id=inspector_id)
    )


@inspector_router.patch(
    path='/{inspector_id}',
    summary='Update inspector',
    dependencies=[Depends(get_current_user)],
)
async def update_inspector(
    inspector_id: int,
    inspector_update_data: UpdateInspectorRequestSchema,
    inspector_service: Annotated[
        InspectorService, Depends(get_service(InspectorService))
    ],
) -> InspectorResponseSchema:
    return InspectorResponseSchema.model_validate(
        await inspector_service.update_inspector(
            inspector_id=inspector_id,
            inspector_update_data=inspector_update_data,
        )
    )

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from core import get_service
from core.constants import INSPECTOR_LICENSE_PREFIX
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_admin_user_from_token
from dto import UploadFileDTO
from schemas import CreateInspectorRequestSchema, InspectorResponseSchema
from services import InspectorService
from services.aws import FileUploadService

logger = logging.getLogger(__name__)

inspector_router = APIRouter()


@inspector_router.get(
    path='/',
    summary='Get all inspectors',
    dependencies=[Depends(get_admin_user_from_token)],
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
    dependencies=[Depends(get_admin_user_from_token)],
)
async def create_inspector(
    inspector_data: CreateInspectorRequestSchema,
    files: Annotated[UploadFile, File()],
    inspector_service: Annotated[
        InspectorService, Depends(get_service(InspectorService))
    ],
    upload_file_service: FileUploadService = Depends(FileUploadService),
) -> InspectorResponseSchema:
    files: list[UploadFileDTO] = await upload_file_service.upload_files(
        files=files,
        prefix=INSPECTOR_LICENSE_PREFIX
    )
    return InspectorResponseSchema.model_validate(
        await inspector_service.create_new_inspector(
            inspector_schema=inspector_data,
            license_files=files,
        )
    )


@inspector_router.get(
    path='/{inspector_id}',
    summary='Get inspector by id',
    dependencies=[Depends(get_admin_user_from_token)],
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

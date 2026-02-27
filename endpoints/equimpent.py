import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from core import get_service
from core.constants import EQUIPMENT_PREFIX
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from schemas import CreateEquipmentRequestSchema, EquipmentResponseSchema
from services import EquipmentService
from services.aws import FileUploadService

logger = logging.getLogger(__name__)

equipment_router = APIRouter()


@equipment_router.get(
    path='/',
    summary='Get all equipments',
    dependencies=[Depends(get_current_user)],
)
async def get_all_equipments(
    pagination: Annotated[PaginationParams, Depends()],
    equipment_service: Annotated[
        EquipmentService, Depends(get_service(EquipmentService))
    ],
) -> PaginatedResponse[EquipmentResponseSchema]:
    items, total = await equipment_service.get_all_equipments(
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


@equipment_router.post(
    path='/',
    summary='Create one equipment with multiple certificate photos',
    dependencies=[Depends(get_current_user)],
)
async def create_equipment(
    equipment_data: Annotated[
        CreateEquipmentRequestSchema,
        Depends(CreateEquipmentRequestSchema.from_form),
    ],
    certificate_files: Annotated[list[UploadFile], File()],
    equipment_service: Annotated[
        EquipmentService, Depends(get_service(EquipmentService))
    ],
    upload_file_service: FileUploadService = Depends(FileUploadService),
) -> EquipmentResponseSchema:
    uploaded_certificates = await upload_file_service.upload_files(
        files=certificate_files, prefix=EQUIPMENT_PREFIX
    )
    return EquipmentResponseSchema.model_validate(
        await equipment_service.create_equipment(
            equipment_schema=equipment_data,
            certificate_files=uploaded_certificates,
        )
    )


@equipment_router.get(
    path='/{equipment_id}',
    summary='Get equipment by id',
    dependencies=[Depends(get_current_user)],
)
async def get_company_by_id(
    equipment_id: int,
    equipment_service: Annotated[
        EquipmentService, Depends(get_service(EquipmentService))
    ],
) -> EquipmentResponseSchema:
    return EquipmentResponseSchema.model_validate(
        await equipment_service.get_equipment_by_id(equipment_id=equipment_id)
    )

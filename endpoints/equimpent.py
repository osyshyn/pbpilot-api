import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from schemas import EquipmentResponseSchema
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


@equipment_router.delete(
    path='/{equipment_id}/certificate-files/{file_index}',
    summary='Delete one certificate file by index',
    dependencies=[Depends(get_current_user)],
)
async def delete_equipment_certificate_file(
    equipment_id: int,
    file_index: int,
    equipment_service: Annotated[
        EquipmentService, Depends(get_service(EquipmentService))
    ],
    upload_file_service: FileUploadService = Depends(FileUploadService),
) -> EquipmentResponseSchema:
    return EquipmentResponseSchema.model_validate(
        await equipment_service.delete_certificate_file(
            equipment_id=equipment_id,
            file_index=file_index,
            file_upload_service=upload_file_service,
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

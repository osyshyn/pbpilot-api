import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from schemas import CreateEquipmentRequestSchema, EquipmentResponseSchema
from services import EquipmentService

logger = logging.getLogger(__name__)

equipment_router = APIRouter()


@equipment_router.get(
    path='/',
    summary='Get all equipments',
    dependencies=[Depends(get_current_user)],
)
async def get_all_clients(
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
    summary='Create a new equipment',
    dependencies=[Depends(get_current_user)],
)
async def create_equipment(
    equipment_data: list[CreateEquipmentRequestSchema],
    equipment_service: Annotated[
        EquipmentService, Depends(get_service(EquipmentService))
    ],
) -> list[EquipmentResponseSchema]:
    return [
        EquipmentResponseSchema.model_validate(equipment)
        for equipment in await equipment_service.create_new_equipments(
            equipment_data=equipment_data
        )
    ]


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

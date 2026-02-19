import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_admin_user_from_token
from schemas import CreateInspectorRequestSchema, InspectorResponseSchema
from schemas.company import (
    CompanyResponseSchema,
    CreateCompanyRequestSchema,
)
from services import CompanyService, InspectorService

logger = logging.getLogger(__name__)

inspector_router = APIRouter()


@inspector_router.post(
    path='/',
    summary='Create a new inspector',
)
async def create_inspector(
    inspector_data: CreateInspectorRequestSchema,
    inspector_service: Annotated[
        InspectorService, Depends(get_service(InspectorService))
    ],
) -> InspectorResponseSchema:
    inspector = await inspector_service.create_new_inspector(
        inspector_data=inspector_data
    )
    return InspectorResponseSchema.model_validate(inspector)

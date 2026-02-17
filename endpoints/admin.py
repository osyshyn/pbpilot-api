import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_admin_user_from_token
from schemas import (
    ClientResponseSchema,
    CreateClientRequestSchema,
    UpdateClientRequestSchema, CreateUserByAdminRequestSchema,
    SignUpResponseSchema,
)
from services import AdminService
from services.client import ClientService

logger = logging.getLogger(__name__)

admin_router = APIRouter(
    dependencies=[Depends(get_admin_user_from_token)],
)

@admin_router.post(
    path='/',
    summary='Create new user',
)
async def create_user(
    user_data: CreateUserByAdminRequestSchema,
    admin_service: Annotated[
        AdminService, Depends(get_service(AdminService))
    ],
) -> SignUpResponseSchema:
    return SignUpResponseSchema.model_validate(
        await admin_service.create_user(user_data=user_data)
    )


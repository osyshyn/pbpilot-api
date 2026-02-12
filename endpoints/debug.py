import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_admin_user_from_token
from schemas import (
    ClientResponseSchema,
    CreateClientRequestSchema,
    UpdateClientRequestSchema, UserResponseSchema,
)
from services import UserService
from services.client import ClientService

logger = logging.getLogger(__name__)

debug_router = APIRouter()


@debug_router.post(
    path='/activate_user/{user_id}',
    description='Activate user by id'
)
async def activate_user(
        user_id: int,
        user_service: Annotated[UserService, Depends(get_service(UserService))],
) -> UserResponseSchema:
    return UserResponseSchema.model_validate(await user_service.activate_user_by_id(user_id=user_id))


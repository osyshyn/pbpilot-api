import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from schemas import (
    UserResponseSchema,
)
from services import UserService

logger = logging.getLogger(__name__)

debug_router = APIRouter()


@debug_router.post(
    path='/activate_user/{user_email}', description='Activate user by id'
)
async def activate_user(
    user_email: str,
    user_service: Annotated[UserService, Depends(get_service(UserService))],
) -> UserResponseSchema:
    return UserResponseSchema.model_validate(
        await user_service.activate_user_by_email(user_email=user_email)
    )

from typing import Annotated

from fastapi import APIRouter, Depends

from config.settings import Settings
from core import get_service
from schemas import SignUpResponseSchema, SignUpRequestSchema
from services import UserService

auth_router = APIRouter()
settings = Settings.load()


@auth_router.post(
    path='/signup',
    description='Create new user.',
    response_model=SignUpResponseSchema,
)
async def signup_user(
    user_data: SignUpRequestSchema,
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> SignUpResponseSchema:
    """Create a new user in the system.

    Args:
        user_data (CreateUserRequestSchema): Schema with new user data.
        service (UserService): Service for user-related operations.

    Returns:
        UserResponseShema: Schema representing the newly created user.

    """
    return await service.create_new_user(user_data=user_data)
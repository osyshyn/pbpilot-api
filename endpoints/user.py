import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile

from core import exception_handler, get_service
from dependencies import get_admin_user_from_token, get_current_user
from models import User
from schemas import UserResponseSchema
from services import UserService

logger = logging.getLogger(__name__)


user_router = APIRouter()


@user_router.get(
    path='/me',
    summary='Get current user profile',
    description=(
        "Retrieve the current authenticated user's profile information "
        'including organization data if available.'
    ),
    tags=['me'],
)
async def get_me(
    token_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UserResponseSchema:
    """Get information about current user.

    Args:
        token_user (User): Current authenticated user from token.
        service: User service.

    Returns:
        UserResponseShema: Schema representing the user with organization data.

    """
    user = await service.get_me(user_id=token_user.id)
    return UserResponseSchema.model_validate(user)


@user_router.delete(
    path='/me',
    summary='Delete current user profile',
    description=(
        "Delete the current authenticated user's profile information."
    ),
    tags=['me'],
)
async def delete_me(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_service(UserService))],
) -> UserResponseSchema:
    """Delete the current authenticated user's profile.

    Args:
        user (User): Current authenticated user from token.
        service (UserService): Service for user-related operations.

    Returns:
        UserResponseShema: Schema representing the deleted user.

    """
    return await service.delete_user_by_id(user_id=user.id)

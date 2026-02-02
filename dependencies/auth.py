from typing import Annotated

from fastapi import Depends
from fastapi.params import Security
from fastapi.security import OAuth2PasswordBearer

from config.settings import Settings
from core import get_service
from exceptions import UserHasNoPermissionPermission
from models import User
from models.user import UserRoleEnum
from services import UserService
from services.auth import AuthService

settings = Settings.load()
oauth_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl=f'Prod/api/{settings.API_VERSION}/auth/login',
)


async def get_current_user(
    token: Annotated[str, Security(oauth_scheme)],
    auth_service: Annotated[AuthService, Depends(get_service(AuthService))],
    user_service: Annotated[UserService, Depends(get_service(UserService))],
) -> User:
    """Get user from token. Role does not matter."""
    user_id = await auth_service.validate_token_for_user(token)
    return await user_service.get_user_by_id(user_id)


async def _get_current_user_by_role(
    user: User,
    role: UserRoleEnum,
) -> User:
    """Get a user with a specific role from a token."""
    if user.role != role:
        raise UserHasNoPermissionPermission
    return user


async def get_admin_user_from_token(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get a user with an admin role from a token.

    Or raise UserHasNoPermissionPermission if role missmatch.
    """
    return await _get_current_user_by_role(current_user, UserRoleEnum.ADMIN)


async def get_manager_user_from_token(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get a user with a manager role from a token."""
    return await _get_current_user_by_role(current_user, UserRoleEnum.MANAGER)


async def get_inspector_user_from_token(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get a user with an inspector role from a token."""
    return await _get_current_user_by_role(current_user, UserRoleEnum.INSPECTOR)


async def get_solo_operator_user_from_token(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get a user with a solo operator role from a token."""
    return await _get_current_user_by_role(
        current_user, UserRoleEnum.SOLO_OPERATOR
    )

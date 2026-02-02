from typing import Annotated

from fastapi import APIRouter, Depends

from config.settings import Settings
from core import get_service
from fastapi.security import OAuth2PasswordRequestForm
from schemas import (
    SignUpResponseSchema,
    SignUpRequestSchema,
    TokenResponseSchemas,
    RefreshTokenRequestSchema
)
from services import UserService, AuthService

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


@auth_router.post(
    path='/login',
    response_model=TokenResponseSchemas,
    summary='User login',
    description=(
            'Authenticate user with email and password to get access to tokens.'
    ),
)
async def login_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        service: Annotated[AuthService, Depends(get_service(AuthService))],
) -> TokenResponseSchemas:
    """Authenticate user and return access and refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): Username and password.
        service (AuthService): Auth service dependency.

    Returns:
        TokenSchemas: Access and refresh tokens with type.

    """
    user = await service.auth_user(
        email=form_data.username,
        password=form_data.password,
    )
    return await service.create_token(
        author_id=user.id, user_role=user.role
    )


@auth_router.post(
    path='/refresh',
    response_model=TokenResponseSchemas,
    summary='Refresh access token',
    description='Get new access and refresh tokens using a valid one.',
)
async def refresh_token(
    refresh_request: Annotated[RefreshTokenRequestSchema, Depends()],
    service: Annotated[AuthService, Depends(get_service(AuthService))],
) -> TokenResponseSchemas:
    """Refresh access and refresh tokens using a valid refresh token.

    Args:
        refresh_request (RefreshTokenRequestSchema): Schema containing
            the refresh token.
        service (AuthService): Auth service dependency.

    Returns:
        TokenSchemas: New access and refresh tokens.

    """
    token: TokenSchemas = await service.refresh_token(
        refresh_token=refresh_request.refresh_token,
    )
    return token



@auth_router.delete(
    path='/logout',
    status_code=204,
    summary='User logout',
    description='Invalidate the provided refresh token to log out the user.',
)
async def logout_user(
    refresh_request: Annotated[RefreshTokenRequestSchema, Depends()],
    service: Annotated[AuthService, Depends(get_service(AuthService))],
) -> None:
    """Invalidate the provided refresh token, logging out the user.

    Args:
        refresh_request (RefreshTokenRequestSchema): Schema containing
            the refresh token to invalidate.
        service (AuthService): Auth service dependency.

    Returns:
        None

    """
    await service.logout_user(refresh_request.refresh_token)

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_current_user
from models import User
from schemas.settings import SettingsResponseSchema
from services.settings import SettingsService

logger = logging.getLogger(__name__)

settings_router = APIRouter(
    dependencies=[Depends(get_current_user)],
)


@settings_router.get(
    path='/',
    summary='Get current user settings',
    description=(
        'Retrieve the current user settings including profile information, '
        'laboratory information, and preferences.'
    ),
    tags=['settings'],
)
async def get_settings(
    token_user: Annotated[User, Depends(get_current_user)],
    settings_service: Annotated[
        SettingsService, Depends(get_service(SettingsService))
    ],
) -> SettingsResponseSchema:
    """Get settings for the current authenticated user.

    Args:
        token_user (User): Current authenticated user from token.
        settings_service (SettingsService): Settings service.

    Returns:
        SettingsResponseSchema: Full settings response.

    """
    return await settings_service.get_settings(user_id=token_user.id)

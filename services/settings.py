import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import UserDAO
from exceptions.user import UserNotFoundByIdException
from models.user import User
from schemas.settings import (
    ProfileInformationSchema,
    SettingsResponseSchema,
)

logger = logging.getLogger(__name__)


class SettingsService(BaseService):
    """Service layer for managing user settings."""

    def __init__(
        self,
        db_session: AsyncSession,
        *,
        user_dao: UserDAO | None = None,
    ):
        """Initialize SettingsService.

        Args:
            db_session (AsyncSession): Database session.
            user_dao (UserDAO | None): Optional UserDAO instance.

        """
        super().__init__(db_session)
        self._user_dao = user_dao or UserDAO(db_session)

    async def get_settings(self, user_id: int) -> SettingsResponseSchema:
        """Get settings for the current user.

        Fetches real data from the User model for profile information.
        Laboratory information and preferences are returned as defaults (stubs).

        Args:
            user_id (int): Current user ID.

        Returns:
            SettingsResponseSchema: Full settings response.

        Raises:
            UserNotFoundByIdException: If user does not exist.

        """
        user: User | None = await self._user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundByIdException

        return SettingsResponseSchema(
            profile_information=ProfileInformationSchema(
                first_name=user.name,
                last_name=user.surname,
                email=user.email,
                lab_results_email=user.email,
                phone_number=user.phone_number or '',
                company_name='',
                business_address='',
            ),
        )

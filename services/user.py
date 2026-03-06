import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import UserDAO
from exceptions import EmailAlreadyRegisteredException
from exceptions.user import UserNotFoundByIdException
from models.user import User, UserRoleEnum
from schemas import (
    SignUpRequestSchema,
)
from services.jwt.hasher import Hasher

logger = logging.getLogger(__name__)


class UserService(BaseService):
    """Service layer for managing user-related operations."""

    def __init__(
        self,
        db_session: AsyncSession,
        *,
        user_dao: UserDAO | None = None,
        hash_service: Hasher | None = None,
    ):
        """Initialize UserService.

        Args:
            db_session (AsyncSession): Database session.
            user_dao (UserDAO | None): Optional UserDAO instance.
            hash_service (Hasher | None): Optional password hasher.

        """
        super().__init__(db_session)
        self._hash_service = hash_service or Hasher()
        self._user_dao = user_dao or UserDAO(db_session)

    async def create_new_user(
        self,
        user_data: SignUpRequestSchema,
    ) -> User:
        """Create a new user in the database.

        Args:
            user_data (CreateUserByAdminRequestSchema): User data
        Returns:
            CreateUserResponseShema: Created user information including
            ID, name, surname, email, active status, and roles

        Note:
            If roles are not provided, defaults to [UserRolesEnum.SOLO_OPERATOR]

        """
        hashed_pass: str = self._hash_service.hash_password(
            user_data.password,
        )
        try:
            # User need to book a call with owner to activate account
            user: User = await self._user_dao.create(
                name=user_data.name,
                surname=user_data.surname,
                email=user_data.email,
                role=UserRoleEnum.SOLO_OPERATOR,
                password=hashed_pass,
                phone_number=user_data.phone_number,
                is_active=False,
                marketing_source=user_data.marketing_source,
                marketing_source_details=user_data.marketing_source_details,
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        await self._session.commit()
        return user

    async def get_user_by_id(self, user_id: int) -> User:
        """Retrieve a user by ID.

        Args:
            user_id (int): User ID.

        Returns:
            User: Retrieved user instance.

        Raises:
            UserNotFoundByIdException: If user does not exist or is inactive.

        """
        user: User | None = await self._user_dao.get_by_id(user_id)
        if not user or not user.is_active:
            raise UserNotFoundByIdException
        return user

    async def get_me(self, user_id: int) -> User:
        """Get current user profile with organization and avatar URL.

        Args:
            user_id: User ID.

        Returns:
            UserResponseShema: User information with organization.

        Raises:
            UserNotFoundByIdException: If user not found.

        """
        return await self.get_user_by_id(user_id)

    async def delete_user_by_id(self, user_id: int) -> User:
        """Delete a user by ID.

        Args:
            current_user (User): Current authenticated user.
            user_id (int): User ID.

        Returns:
            User: Deleted user.

        Raises:
            UserNotFoundByIdException: If user does not exist.

        """
        user: User | None = await self._user_dao.delete_by_id(user_id)
        if not user:
            raise UserNotFoundByIdException
        await self._session.commit()
        return user

    async def activate_user_by_email(self, user_email: str) -> User:
        user: User | None = await self._user_dao.activate_user_by_email(
            email=user_email
        )
        if not user:
            raise UserNotFoundByIdException
        await self._session.commit()
        return user

import logging

from core import BaseService
from dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import EmailAlreadyRegisteredException
from exceptions.user import UserNotFoundByIdException
from models.user import UserRoleEnum, User
from schemas import SignUpRequestSchema, SignUpResponseSchema, \
    UserResponseSchema
from services.jwt.hasher import Hasher
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class UserService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            *,
            user_dao: UserDAO | None = None,
            hash_service: Hasher | None = None,
    ):
        super().__init__(db_session)
        self._hash_service = hash_service or Hasher()
        self._user_dao = user_dao or UserDAO(db_session)

    async def create_new_user(
        self,
        user_data: SignUpRequestSchema,
    ) -> SignUpResponseSchema:
        hashed_pass: str = self._hash_service.hash_password(
            user_data.password,
        )
        try:
            user: User = await self._user_dao.create(
                name=user_data.name,
                surname=user_data.surname,
                email=user_data.email,
                role=UserRoleEnum.SOLO_OPERATOR,
                password=hashed_pass,
                phone_number=user_data.phone_number,
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        await self._session.commit()
        return SignUpResponseSchema.model_validate(user)

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

    async def delete_user_by_id(
            self, user_id: int
    ) -> User:
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

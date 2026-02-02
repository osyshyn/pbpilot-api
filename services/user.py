import logging

from core import BaseService
from dao import UserDAO
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import EmailAlreadyRegisteredException
from models.user import UserRoleEnum, User
from schemas import SignUpRequestSchema, SignUpResponseSchema
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

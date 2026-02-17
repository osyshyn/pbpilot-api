import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import ClientDAO, UserDAO
from exceptions import (
    ClientEmailAlreadyRegisteredException,
    ClientNotFoundException, EmailAlreadyRegisteredException,
)
from models import Client
from models.user import UserRoleEnum, User, MarketingSourceEnum
from schemas import CreateClientRequestSchema, UpdateClientRequestSchema, \
    CreateUserByAdminRequestSchema
from services.jwt.hasher import Hasher
import secrets
import string

logger = logging.getLogger(__name__)


class AdminService(BaseService):
    _PASSWORD_LENGTH = 15

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

    @staticmethod
    def _generate_random_password() -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}<>?"
        return "".join(
            secrets.choice(alphabet) for _ in range(
                AdminService._PASSWORD_LENGTH
            )
        )

    async def create_user(
            self,
            user_data: CreateUserByAdminRequestSchema
    ):
        try:
            # User created from admin doesn't need to call with an owner,
            # so we can create it with active status
            user: User = await self._user_dao.create(
                name=user_data.name,
                surname=user_data.surname,
                email=user_data.email,
                role=UserRoleEnum.SOLO_OPERATOR,
                password=self._hash_service.hash_password(
                    self._generate_random_password(),
                ),
                phone_number=user_data.phone_number,
                is_active=True,
                marketing_source=MarketingSourceEnum.REFERRAL,
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        await self._session.commit()
        return user

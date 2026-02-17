import logging
import secrets
import string

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import UserDAO
from exceptions import (
    EmailAlreadyRegisteredException,
)
from exceptions.user import UserNotFoundByIdException
from models.user import MarketingSourceEnum, User, UserRoleEnum
from schemas import (
    CreateUserByAdminRequestSchema, AssignFreeReportsRequestSchema,
)
from services.email import EmailService
from services.jwt.hasher import Hasher

logger = logging.getLogger(__name__)


class AdminService(BaseService):
    _PASSWORD_LENGTH = 15

    def __init__(
            self,
            db_session: AsyncSession,
            *,
            user_dao: UserDAO | None = None,
            hash_service: Hasher | None = None,
            email_service: EmailService | None = None,
    ):
        super().__init__(db_session)
        self._hash_service = hash_service or Hasher()
        self._user_dao = user_dao or UserDAO(db_session)
        self._email_service = email_service or EmailService()

    @staticmethod
    def _generate_random_password() -> str:
        alphabet = (
                string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}<>?'
        )
        return ''.join(
            secrets.choice(alphabet)
            for _ in range(AdminService._PASSWORD_LENGTH)
        )

    async def create_user(
            self, user_data: CreateUserByAdminRequestSchema
    ) -> User:
        email: str = user_data.email
        password: str = self._generate_random_password()
        try:
            # User created from admin doesn't need to call with an owner,
            # so we can create it with active status
            user: User = await self._user_dao.create(
                name=user_data.name,
                surname=user_data.surname,
                email=email,
                role=UserRoleEnum.SOLO_OPERATOR,
                password=self._hash_service.hash_password(
                    password,
                ),
                phone_number=user_data.phone_number,
                is_active=True,
                marketing_source=MarketingSourceEnum.REFERRAL,
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        await self._session.commit()
        await self._email_service.send_registration_email(
            email=email,
            password=password,
        )
        return user

    async def assign_free_reports(
            self,
            user_id: int,
            reports_data: AssignFreeReportsRequestSchema,
    ) -> User:
        user: User | None= await self._user_dao.assign_free_reports_by_id(
            user_id,
            reports_data.report_amount
        )
        if not user:
            raise UserNotFoundByIdException
        await self._session.commit()
        return user

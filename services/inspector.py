import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import UserDAO, InspectorDAO
from exceptions import EmailAlreadyRegisteredException
from exceptions.user import UserNotFoundByIdException
from models import Inspector
from models.user import User, UserRoleEnum
from schemas import (
    CreateInspectorRequestSchema,
)

logger = logging.getLogger(__name__)


class InspectorService(BaseService):

    def __init__(
            self,
            db_session: AsyncSession,
            *,
            inspector_dao: InspectorDAO | None = None,
    ):
        super().__init__(db_session)
        self._inspector_dao = inspector_dao or InspectorDAO(db_session)

    async def create_new_inspector(
            self,
            inspector_data: CreateInspectorRequestSchema,
    ) -> Inspector:
        try:
            inspector: Inspector = await self._inspector_dao.create(
                name=inspector_data.name,
                surname=inspector_data.surname,
                email=inspector_data.email,
                phone_number=inspector_data.phone_number,
                license_number=inspector_data.license_number,
                licence_type=inspector_data.licence_type,
                issue_date=inspector_data.issue_date,
                expiration_date=inspector_data.expiration_date,
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        await self._session.commit()
        return inspector

    async def get_inspector_by_id(self, inspector_id: int) -> Inspector:
        inspector: Inspector | None = await self._inspector_dao.get_by_id(
            inspector_id)
        if not inspector or not inspector.is_active:
            raise UserNotFoundByIdException
        return inspector

    async def get_all_inspectors(
            self,
            pagination: PaginationParams
    ) -> tuple[list[Inspector], int]:
        return await self._inspector_dao.get_all(
            page=pagination.page, limit=pagination.size
        )

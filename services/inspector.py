import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import InspectorDAO
from dto import CreateInspectorDTO, InspectorDashboardDTO, UploadFileDTO
from exceptions import EmailAlreadyRegisteredException
from exceptions.user import UserNotFoundByIdException
from models import Inspector
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
        license_files: list[UploadFileDTO] | UploadFileDTO,
        inspector_schema: CreateInspectorRequestSchema,
    ) -> Inspector:
        license_file: UploadFileDTO = (
            license_files
            if isinstance(license_files, UploadFileDTO)
            else license_files[0]
        )
        try:
            inspector_data: CreateInspectorDTO = (
                CreateInspectorDTO(  # TODO: User mapper here
                    name=inspector_schema.name,
                    surname=inspector_schema.surname,
                    email=inspector_schema.email,
                    phone_number=inspector_schema.phone_number,
                    license_number=inspector_schema.license_number,
                    licence_type=inspector_schema.licence_type,
                    issue_date=inspector_schema.issue_date,
                    expiration_date=inspector_schema.expiration_date,
                    license_image_key=license_file.key,
                )
            )
            inspector: Inspector = await self._inspector_dao.create(
                inspector_data=inspector_data
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        await self._session.commit()
        return inspector

    async def get_inspector_by_id(self, inspector_id: int) -> Inspector:
        inspector: Inspector | None = await self._inspector_dao.get_by_id(
            inspector_id
        )
        if not inspector or not inspector.is_active:
            raise UserNotFoundByIdException
        return inspector

    async def get_all_inspectors(
        self, pagination: PaginationParams
    ) -> tuple[list[Inspector], int]:
        return await self._inspector_dao.get_all(
            page=pagination.page, limit=pagination.size
        )

    async def get_inspectors_dashboard(
        self,
        user_id: int,
    ) -> InspectorDashboardDTO:
        return await self._inspector_dao.get_inspectors_dashboard(user_id=user_id)

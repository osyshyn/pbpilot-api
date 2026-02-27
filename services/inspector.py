import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService, SchemaMapper
from core.pagination import PaginationParams
from dao import EquipmentDAO, InspectorDAO
from dto import (
    CreateEquipmentDTO,
    CreateInspectorDTO,
    InspectorDashboardDTO,
    UploadFileDTO,
)
from exceptions import EmailAlreadyRegisteredException, FileUploadException
from exceptions.user import UserNotFoundByIdException
from models import Inspector
from schemas import (
    CreateEquipmentRequestSchema,
    CreateInspectorRequestSchema,
    UpdateInspectorRequestSchema,
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

    async def create_new_inspector_with_equipment(
        self,
        license_files: list[UploadFileDTO] | UploadFileDTO,
        certificates_files: list[UploadFileDTO] | UploadFileDTO,
        inspector_schema: CreateInspectorRequestSchema,
        equipment_data: list[CreateEquipmentRequestSchema],
    ) -> Inspector:
        if isinstance(license_files, UploadFileDTO):
            license_files_list: list[UploadFileDTO] = [license_files]
        else:
            license_files_list = license_files

        if isinstance(certificates_files, UploadFileDTO):
            certificates_files_list: list[UploadFileDTO] = [certificates_files]
        else:
            certificates_files_list = certificates_files

        if len(equipment_data) != len(certificates_files_list):
            # One equipment must strictly correspond to one certificate photo
            raise FileUploadException()

        try:
            inspector_data: CreateInspectorDTO = SchemaMapper.to_dto(
                CreateInspectorDTO,
                inspector_schema,
                license_image_key=license_files_list[0].key,
            )
            inspector: Inspector = await self._inspector_dao.create(
                inspector_data=inspector_data
            )

            equipment_dao = EquipmentDAO(self._session)

            equipments_dto: list[CreateEquipmentDTO] = [
                SchemaMapper.to_dto(
                    CreateEquipmentDTO,
                    equipment_schema,
                    training_certificate_key=certificates_files_list[idx].key,
                )
                for idx, equipment_schema in enumerate(equipment_data)
            ]

            await equipment_dao.create_bulk(equipments=equipments_dto)
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

    async def update_inspector(
        self,
        inspector_id: int,
        inspector_update_data: UpdateInspectorRequestSchema,
    ) -> Inspector:
        try:
            inspector = await self._inspector_dao.update_by_id(
                inspector_id=inspector_id,
                update_data=inspector_update_data.model_dump(
                    exclude_unset=True
                ),
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        if not inspector:
            raise UserNotFoundByIdException
        await self._session.commit()
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
        return await self._inspector_dao.get_inspectors_dashboard(
            user_id=user_id
        )

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService, SchemaMapper
from core.constants import EQUIPMENT_FIELD_TRAINING_CERTIFICATE_KEYS
from core.pagination import PaginationParams
from dao import EquipmentDAO
from dto import CreateEquipmentDTO, UploadFileDTO
from exceptions import (
    CertificateFileIndexOutOfRangeException,
    EquipmentNotFoundException,
)
from models import Equipment
from schemas import CreateEquipmentRequestSchema
from services.aws import FileUploadService

logger = logging.getLogger(__name__)


class EquipmentService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        equipment_dao: EquipmentDAO | None = None,
    ):
        super().__init__(db_session)
        self._equipment_dao = equipment_dao or EquipmentDAO(db_session)

    async def create_equipment(
        self,
        inspector_id: int,
        equipment_schema: CreateEquipmentRequestSchema,
        certificate_files: list[UploadFileDTO],
    ) -> Equipment:
        """Create one equipment for an inspector with multiple certificate photos."""
        if not certificate_files:
            raise ValueError('At least one certificate file is required')
        training_certificate_keys = [f.key for f in certificate_files]
        equipment_dto: CreateEquipmentDTO = SchemaMapper.to_dto(
            CreateEquipmentDTO,
            equipment_schema,
            inspector_id=inspector_id,
            training_certificate_keys=training_certificate_keys,
        )
        equipments: list[Equipment] = await self._equipment_dao.create_bulk(
            equipments=[equipment_dto]
        )
        await self._session.commit()
        return equipments[0]

    async def create_new_equipments(
        self,
        inspector_id: int,
        equipment_data: list[CreateEquipmentRequestSchema],
    ) -> list[Equipment]:
        equipments_dto: list[CreateEquipmentDTO] = [
            SchemaMapper.to_dto(
                CreateEquipmentDTO,
                equipment,
                inspector_id=inspector_id,
            )
            for equipment in equipment_data
        ]
        equipments: list[Equipment] = await self._equipment_dao.create_bulk(
            equipments=equipments_dto
        )
        await self._session.commit()
        return equipments

    async def get_equipment_by_id(self, equipment_id: int) -> Equipment:
        equipment: Equipment | None = await self._equipment_dao.get_by_id(
            equipment_id=equipment_id
        )
        if not equipment:
            raise EquipmentNotFoundException()
        return equipment

    async def get_all_equipments(
        self, pagination: PaginationParams
    ) -> tuple[list[Equipment], int]:
        return await self._equipment_dao.get_all(
            page=pagination.page, limit=pagination.size
        )

    async def delete_certificate_file(
        self,
        equipment_id: int,
        file_index: int,
        file_upload_service: FileUploadService,
    ) -> Equipment:
        """Remove one certificate file by index: delete from S3 and update DB."""
        equipment = await self.get_equipment_by_id(equipment_id)
        keys: list[str] = list(equipment.training_certificate_keys or [])
        if file_index < 0 or file_index >= len(keys):
            raise CertificateFileIndexOutOfRangeException()
        key_to_delete = keys[file_index]
        file_upload_service.delete_file(key_to_delete)
        new_keys = [k for i, k in enumerate(keys) if i != file_index]
        updated = await self._equipment_dao.update_by_id(
            equipment_id,
            update_data={
                EQUIPMENT_FIELD_TRAINING_CERTIFICATE_KEYS: new_keys or None,
            },
        )
        await self._session.commit()
        if updated:
            await self._session.refresh(updated)
            return updated
        return equipment

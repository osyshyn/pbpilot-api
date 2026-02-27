import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService, SchemaMapper
from core.pagination import PaginationParams
from dao import EquipmentDAO
from dto import CreateEquipmentDTO, UploadFileDTO
from models import Equipment
from schemas import CreateEquipmentRequestSchema

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
            raise ValueError('ChangeItLater')
        return equipment

    async def get_all_equipments(
        self, pagination: PaginationParams
    ) -> tuple[list[Equipment], int]:
        return await self._equipment_dao.get_all(
            page=pagination.page, limit=pagination.size
        )

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import EquipmentDAO
from exceptions import EmailAlreadyRegisteredException
from exceptions.user import UserNotFoundByIdException
from models import Equipment
from schemas import (
    CreateEquipmentRequestSchema,
)

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

    async def create_new_equipment(
            self,
            equipment_data: CreateEquipmentRequestSchema,
    ) -> Equipment:
        equipment: Equipment = await self._equipment_dao.create(
            name=equipment_data.name,
            manufacturer=equipment_data.manufacturer,
            model=equipment_data.model,
            serial_number=equipment_data.serial_number,
            mode=equipment_data.mode,
            date_of_radioactive_source=equipment_data.date_of_radioactive_source,
            training_certificate_key=equipment_data.training_certificate_key,
        )
        await self._session.commit()
        return equipment

    async def get_equipment_by_id(self, equipment_id: int) -> Equipment:
        equipment: Equipment | None = await self._equipment_dao.get_by_id(
            equipment_id=equipment_id
        )
        return equipment

    async def get_all_equipments(
            self, pagination: PaginationParams
    ) -> tuple[list[Equipment], int]:
        return await self._equipment_dao.get_all(
            page=pagination.page, limit=pagination.size
        )

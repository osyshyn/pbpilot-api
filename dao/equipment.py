from datetime import date

from sqlalchemy import select

from core.dao import BaseDAO
from models import Equipment
from models.equipment import OperationModeEnum


class EquipmentDAO(BaseDAO):
    async def create(
            self,
            *,
            name: str,
            manufacturer: str,
            model: str,
            serial_number: str,
            mode: OperationModeEnum,
            date_of_radioactive_source: date | None = None,
            training_certificate_key: str | None = None,

    ) -> Equipment:
        equipment = Equipment(
            name=name,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            mode=mode,
            date_of_radioactive_source=date_of_radioactive_source,
            training_certificate_key=training_certificate_key,
        )
        self._session.add(equipment)
        await self._session.flush()
        await self._session.refresh(equipment)
        return equipment

    async def get_all(
            self, page: int, limit: int
    ) -> tuple[list[Equipment], int]:
        query = select(Equipment)
        return await self.paginate(query=query, page=page, limit=limit)

    async def get_by_id(self, equipment_id: int) -> Equipment | None:
        stmt = select(Equipment).where(
            Equipment.id == equipment_id, Equipment.is_active == True
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

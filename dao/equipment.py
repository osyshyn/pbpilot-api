from sqlalchemy import select

from core.dao import BaseDAO
from dto import CreateEquipmentDTO
from models import Equipment


class EquipmentDAO(BaseDAO):
    async def create_bulk(
        self, equipments: list[CreateEquipmentDTO]
    ) -> list[Equipment]:
        db_equipments: list[Equipment] = [
            Equipment(
                name=equipment.name,
                manufacturer=equipment.manufacturer,
                model=equipment.model,
                serial_number=equipment.serial_number,
                mode=equipment.mode,
                date_of_radioactive_source=equipment.date_of_radioactive_source,
                training_certificate_keys=equipment.training_certificate_keys,
            )
            for equipment in equipments
        ]
        self._session.add_all(db_equipments)
        await self._session.flush()
        return db_equipments

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

from typing import Any

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
                inspector_id=equipment.inspector_id,
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

    async def get_all_by_inspector_id(
        self,
        inspector_id: int,
    ) -> list[Equipment]:
        stmt = select(Equipment).where(
            Equipment.inspector_id == inspector_id,
            Equipment.is_active == True,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_by_id(
        self,
        equipment_id: int,
        update_data: dict[str, Any],
    ) -> Equipment | None:
        equipment = await self.get_by_id(equipment_id)
        if not equipment:
            return None
        for key, value in update_data.items():
            if hasattr(equipment, key):
                setattr(equipment, key, value)
        await self._session.flush()
        await self._session.refresh(equipment)
        return equipment

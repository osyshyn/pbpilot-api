from datetime import date

from sqlalchemy import select

from core.dao import BaseDAO
from dto import CreateInspectorDTO
from models import Inspector
from models.inspector import LicenseTypeEnum


class InspectorDAO(BaseDAO):
    """DAO for User model."""

    async def create(
            self,
            *,
            inspector_data: CreateInspectorDTO,
    ) -> Inspector:
        inspector = Inspector(
            name=inspector_data.name,
            surname=inspector_data.surname,
            email=inspector_data.email,
            phone_number=inspector_data.phone_number,
            license_number=inspector_data.license_number,
            licence_type=inspector_data.licence_type,
            issue_date=inspector_data.issue_date,
            expiration_date=inspector_data.expiration_date,
            license_image_key=inspector_data.license_image_key,
        )
        self._session.add(inspector)
        await self._session.flush()
        await self._session.refresh(inspector)
        return inspector

    async def get_all(
            self, page: int, limit: int
    ) -> tuple[list[Inspector], int]:
        query = select(Inspector)
        return await self.paginate(query=query, page=page, limit=limit)

    async def get_by_id(self, inspector_id: int) -> Inspector | None:
        stmt = select(Inspector).where(
            Inspector.id == inspector_id, Inspector.is_active == True
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

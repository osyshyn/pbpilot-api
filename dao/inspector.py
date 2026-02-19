from datetime import date

from sqlalchemy import select

from core.dao import BaseDAO
from models import Inspector
from models.inspector import LicenseTypeEnum


class InspectorDAO(BaseDAO):
    """DAO for User model."""

    async def create(
        self,
        *,
        name: str,
        surname: str,
        email: str,
        phone_number: str | None = None,
        license_number: str,
        licence_type: LicenseTypeEnum,
        issue_date: date,
        expiration_date: date,
    ) -> Inspector:
        inspector = Inspector(
            name=name,
            surname=surname,
            email=email,
            phone_number=phone_number,
            license_number=license_number,
            licence_type=licence_type,
            issue_date=issue_date,
            expiration_date=expiration_date,
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

    async def get_by_id(self, client_id: int) -> Inspector | None:
        stmt = select(Inspector).where(
            Inspector.id == client_id, Inspector.is_active == True
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

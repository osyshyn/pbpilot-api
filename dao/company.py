from core.dao import BaseDAO
from models import Company


class CompanyDAO(BaseDAO):
    """DAO for Client model."""

    async def create(
        self,
    ) -> Company:
        pass
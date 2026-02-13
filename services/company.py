import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import CompanyDAO
from models import Company
from schemas import CreateClientRequestSchema

logger = logging.getLogger(__name__)


class CompanyService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            *,
            company_dao: CompanyDAO | None = None,
    ):
        super().__init__(db_session)
        self._company_dao = company_dao or CompanyDAO(db_session)

    async def create_company(
            self, company_data: CreateClientRequestSchema
    ) -> Company:
        pass

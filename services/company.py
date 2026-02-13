import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import CompanyDAO
from exceptions import CompanyAlreadyExistsNotFoundException
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
        try:
            company = await self._company_dao.create(
                company_name=company_data.company_name,
                phone_number=company_data.phone_number,
                address=company_data.address,
                timezone=company_data.timezone,
                logo_key=company_data.logo_key,
                tax_state=company_data.tax_state,
                tax_percentage=company_data.tax_percentage,
            )
        except IntegrityError:
            raise CompanyAlreadyExistsNotFoundException from None
        await self._session.commit()
        return company

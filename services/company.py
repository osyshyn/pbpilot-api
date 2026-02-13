import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import CompanyDAO
from exceptions import (
    CompanyAlreadyExistsException,
    CompanyNotFoundException,
)
from models import Company
from schemas import CreateCompanyRequestSchema

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
        self, company_data: CreateCompanyRequestSchema
    ) -> Company:
        """Create a company with its working hours schedule."""
        try:
            created = await self._company_dao.create_with_schedule(
                company_name=company_data.company_name,
                phone_number=company_data.phone_number,
                address=company_data.address,
                timezone=company_data.timezone,
                logo_key=company_data.logo_key,
                tax_state=company_data.tax_state,
                tax_percentage=company_data.tax_percentage,
                schedule_data=company_data.schedule, # TODO: Consider moving from pydantic to dto
            )
        except IntegrityError:
            raise CompanyAlreadyExistsException from None
        await self._session.commit()
        company = await self._company_dao.get_by_id_with_schedule(created.id)
        if not company:
            raise CompanyNotFoundException
        return company

    async def get_company_by_id(self, company_id: int) -> Company:
        """Get single company with its schedule."""
        company = await self._company_dao.get_by_id_with_schedule(company_id)
        if not company:
            raise CompanyNotFoundException
        return company

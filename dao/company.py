from core.dao import BaseDAO
from models import Company


class CompanyDAO(BaseDAO):
    """DAO for Client model."""

    async def create(
            self,
            *,
            company_name: str,
            phone_number: str,
            address: str,
            timezone: str,
            logo_key: str,
            tax_state: str,
            tax_percentage: float,
    ) -> Company:
        company = Company(
            company_name=company_name,
            phone_number=phone_number,
            address=address,
            timezone=timezone,
            logo_key=logo_key,
            tax_state=tax_state,
            tax_percentage=tax_percentage,
        )
        self._session.add(company)
        await self._session.flush()
        await self._session.refresh(company)
        return company

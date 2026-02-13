from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.dao import BaseDAO
from models import Company, CompanySchedule
from schemas.company import CreateCompanyScheduleItemRequestSchema


class CompanyDAO(BaseDAO):
    """DAO for Company model."""

    async def create_with_schedule(
        self,
        *,
        company_name: str,
        phone_number: str | None,
        address: str,
        timezone: str,
        logo_key: str | None,
        tax_state: str,
        tax_percentage: float,
        schedule_data: list[CreateCompanyScheduleItemRequestSchema],
    ) -> Company:
        """Create a company with its working hours schedule."""
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

        for item in schedule_data:
            schedule = CompanySchedule(
                company_id=company.id,
                day_of_week=item.day_of_week,
                start_time=item.start_time,
                end_time=item.end_time,
            )
            self._session.add(schedule)

        await self._session.flush()
        await self._session.refresh(company)
        return company

    async def get_by_id_with_schedule(self, company_id: int) -> Company | None:
        """Get company by id with schedule loaded."""
        stmt = (
            select(Company)
            .where(Company.id == company_id)
            .options(selectinload(Company.schedule))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

from collections.abc import Sequence

from sqlalchemy import select

from core.dao import BaseDAO
from models import PricingPlan


class PricingPlanDAO(BaseDAO):
    """Data Access Object for PricingPlan."""

    async def get_all(self) -> Sequence[PricingPlan]:
        """Return all pricing plans.

        Returns:
            list[PricingPlan]: List of all pricing plan records.

        """
        stmt = select(PricingPlan)
        result = await self._session.execute(stmt)
        return result.scalars().all()

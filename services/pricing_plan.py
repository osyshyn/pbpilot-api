import logging
from typing import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from dao import UserDAO, PricingPlanDAO
from exceptions import EmailAlreadyRegisteredException
from exceptions.user import UserNotFoundByIdException
from models import PricingPlan
from models.user import User, UserRoleEnum
from schemas import (
    SignUpRequestSchema,
    SignUpResponseSchema,
)
from services.jwt.hasher import Hasher

logger = logging.getLogger(__name__)


class PricingPlanService(BaseService):

    def __init__(
        self,
        db_session: AsyncSession,
        *,
        pricing_plan_dao: PricingPlanDAO | None = None,
    ):
        super().__init__(db_session)
        self._pricing_plan_dao = pricing_plan_dao or PricingPlanDAO(db_session)

    async def get_all_pricing_plans(self) -> Sequence[PricingPlan]:
        return await self._pricing_plan_dao.get_all()
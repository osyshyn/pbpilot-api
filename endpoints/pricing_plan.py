import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_current_user
from schemas import (
    PricingPlanListResponseSchema,
    PricingPlanResponseSchema,
)
from services import PricingPlanService

logger = logging.getLogger(__name__)

pricing_plan_router = APIRouter()


@pricing_plan_router.get(
    path='/',
    summary='Get all pricing plans in system',
    description='Retrieve all pricing plans in the system.',
    dependencies=[Depends(get_current_user)],
)
async def get_pricing_plans(
    service: Annotated[
        PricingPlanService, Depends(get_service(PricingPlanService))
    ],
) -> PricingPlanListResponseSchema:
    return PricingPlanListResponseSchema(
        items=[
            PricingPlanResponseSchema.model_validate(p)
            for p in await service.get_all_pricing_plans()
        ]
    )

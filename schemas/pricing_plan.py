from typing import Annotated

from pydantic import Field

from core import BaseModelSchema
from models.pricing_plan import BillingPeriodEnum, CurrencyEnum, UserPlanEnum


class PricingPlanResponseSchema(BaseModelSchema):
    plan: Annotated[
        UserPlanEnum,
        Field(
            description='User plan',
            examples=[UserPlanEnum.ENTERPRISE],
        ),
    ]
    period: Annotated[
        BillingPeriodEnum,
        Field(
            description='Billing period',
            examples=[BillingPeriodEnum.MONTHLY],
        ),
    ]
    price: Annotated[
        int,
        Field(
            description='Price per period',
            examples=[100],
        ),
    ]
    currency: Annotated[
        CurrencyEnum,
        Field(
            description='Currency',
            examples=[CurrencyEnum.USD],
        ),
    ]


class PricingPlanListResponseSchema(BaseModelSchema):
    items: list[PricingPlanResponseSchema]

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_current_user
from schemas.company import (
    CompanyResponseSchema,
    CreateCompanyRequestSchema,
    UpdateCompanyScheduleRequestSchema,
)
from services import CompanyService

logger = logging.getLogger(__name__)

company_router = APIRouter()


@company_router.post(
    path='/',
    summary='Create a new company',
)
async def create_company(
    company_data: CreateCompanyRequestSchema,
    company_service: Annotated[
        CompanyService, Depends(get_service(CompanyService))
    ],
) -> CompanyResponseSchema:
    company = await company_service.create_company(company_data=company_data)
    return CompanyResponseSchema.model_validate(company)


@company_router.get(
    path='/{company_id}',
    summary='Get company by id',
    dependencies=[Depends(get_current_user)],
)
async def get_company_by_id(
    company_id: int,
    company_service: Annotated[
        CompanyService, Depends(get_service(CompanyService))
    ],
) -> CompanyResponseSchema:
    company = await company_service.get_company_by_id(company_id=company_id)
    return CompanyResponseSchema.model_validate(company)


@company_router.put(
    path='/{company_id}/schedule',
    summary='Update working hours for a company',
    description=(
        'Fully replaces the existing working-hours schedule for the company. '
        'Days not included in the request body are treated as non-working days.'
    ),
    dependencies=[Depends(get_current_user)],
)
async def update_company_schedule(
    company_id: int,
    schedule_data: UpdateCompanyScheduleRequestSchema,
    company_service: Annotated[
        CompanyService, Depends(get_service(CompanyService))
    ],
) -> CompanyResponseSchema:
    company = await company_service.update_schedule(
        company_id=company_id,
        schedule_data=schedule_data,
    )
    return CompanyResponseSchema.model_validate(company)

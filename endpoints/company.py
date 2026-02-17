import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_admin_user_from_token
from schemas.company import (
    CompanyResponseSchema,
    CreateCompanyRequestSchema,
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
    dependencies=[Depends(get_admin_user_from_token)]
)
async def get_company_by_id(
    company_id: int,
    company_service: Annotated[
        CompanyService, Depends(get_service(CompanyService))
    ],
) -> CompanyResponseSchema:
    company = await company_service.get_company_by_id(company_id=company_id)
    return CompanyResponseSchema.model_validate(company)

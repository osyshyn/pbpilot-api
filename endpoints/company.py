import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from schemas import CreateCompanyRequestSchema

logger = logging.getLogger(__name__)

company_router = APIRouter()


@company_router.post(
    path='/',
    summary='Create a new company',
)
async def create_company(
        company_data: CreateCompanyRequestSchema,
        project_service: Annotated[
            CompanyService, Depends(get_service(CompanyService))
        ]
        # TODO: Add avatar
): # TODO: Respose model
    await project_service.create_company(company_data=company_data)

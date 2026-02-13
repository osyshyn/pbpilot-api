import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from services.client import ClientService

logger = logging.getLogger(__name__)

company_router = APIRouter()


@company_router.post(
    path='/',
    summary='Create a new company',
)
async def create_company(
):
    pass


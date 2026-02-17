import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_admin_user_from_token
from schemas import (
    AssignFreeReportsRequestSchema,
    AssignFreeReportsResponseSchema,
    CreateUserByAdminRequestSchema,
    SignUpResponseSchema,
)
from services import AdminService

logger = logging.getLogger(__name__)

admin_router = APIRouter(
    dependencies=[Depends(get_admin_user_from_token)],
)


@admin_router.post(
    path='/user/',
    summary='Create new user',
)
async def create_user(
    user_data: CreateUserByAdminRequestSchema,
    admin_service: Annotated[AdminService, Depends(get_service(AdminService))],
) -> SignUpResponseSchema:
    return SignUpResponseSchema.model_validate(
        await admin_service.create_user(user_data=user_data)
    )


@admin_router.patch(
    path='/user/{user_id}',
    summary='Assign free reports',
)
async def assign_free_reports(
    user_id: int,
    reports_data: AssignFreeReportsRequestSchema,
    admin_service: Annotated[AdminService, Depends(get_service(AdminService))],
) -> AssignFreeReportsResponseSchema:
    return AssignFreeReportsResponseSchema.model_validate(
        await admin_service.assign_free_reports(
            user_id=user_id, reports_data=reports_data
        )
    )

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from schemas import (
    AssignFreeReportsRequestSchema,
    AssignFreeReportsResponseSchema,
    CreateUserByAdminRequestSchema,
    SignUpResponseSchema,
    UserResponseSchema,
)
from services import AdminService

logger = logging.getLogger(__name__)

admin_router = APIRouter(
    dependencies=[Depends(get_current_user)],
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


@admin_router.get(
    path='/user/',
    summary='Get all users',
)
async def get_all_users(
    pagination: Annotated[PaginationParams, Depends()],
    admin_service: Annotated[AdminService, Depends(get_service(AdminService))],
) -> PaginatedResponse[UserResponseSchema]:
    items, total = await admin_service.get_users(pagination=pagination)
    pages = (total + pagination.size - 1) // pagination.size
    return PaginatedResponse(
        items=items,  # type: ignore
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )

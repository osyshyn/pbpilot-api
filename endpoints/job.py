import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from schemas import (
    CreateJobRequestSchema,
    JobDetailsResponseSchema,
    JobResponseSchema,
)
from services.job import JobService

logger = logging.getLogger(__name__)

job_router = APIRouter()


@job_router.post(
    path='/',
    summary='Create job',
    dependencies=[Depends(get_current_user)],
)
async def create_job(
    job_data: CreateJobRequestSchema,
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> JobResponseSchema:
    return JobResponseSchema.model_validate(
        await job_service.create_job(data=job_data)
    )


@job_router.get(
    path='/',
    summary='Get all jobs',
    dependencies=[Depends(get_current_user)],
)
async def get_all_jobs(
    pagination: Annotated[PaginationParams, Depends()],
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> PaginatedResponse[JobResponseSchema]:
    items, total = await job_service.get_all_jobs(pagination=pagination)
    pages = (total + pagination.size - 1) // pagination.size
    return PaginatedResponse(
        items=items,  # type: ignore[arg-type]
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )


@job_router.get(
    path='/{job_id}',
    summary='Get job by id',
    dependencies=[Depends(get_current_user)],
)
async def get_job_by_id(
    job_id: int,
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> JobResponseSchema:
    job = await job_service.get_job_by_id(job_id=job_id)
    return JobResponseSchema.model_validate(job)


@job_router.get(
    path='/{job_id}/details',
    summary='Get job details by id',
    dependencies=[Depends(get_current_user)],
)
async def get_job_details(
    job_id: int,
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> JobDetailsResponseSchema:
    details_dto = await job_service.get_job_details(job_id=job_id)
    return JobDetailsResponseSchema.model_validate(details_dto)


@job_router.delete(
    path='/{job_id}',
    summary='Delete job by id',
    dependencies=[Depends(get_current_user)],
)
async def delete_job_by_id(
    job_id: int,
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> JobResponseSchema:
    job = await job_service.delete_job_by_id(job_id=job_id)
    return JobResponseSchema.model_validate(job)

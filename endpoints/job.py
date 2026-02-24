import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service
from dependencies import get_admin_user_from_token
from schemas import CreateJobRequestSchema, JobResponseSchema
from services.job import JobService

logger = logging.getLogger(__name__)

job_router = APIRouter()


@job_router.post(
    path='/',
    summary='Create job',
    dependencies=[Depends(get_admin_user_from_token)],
)
async def create_job(
    job_data: CreateJobRequestSchema,
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> JobResponseSchema:
    return JobResponseSchema.model_validate(await job_service.create_job(data=job_data))


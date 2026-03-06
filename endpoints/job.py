import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from core import get_service
from core.pagination import PaginatedResponse, PaginationParams
from dependencies import get_current_user
from schemas import (
    AssignInspectorRequestSchema,
    CreateJobRequestSchema,
    JobDetailsResponseSchema,
    JobListFiltersSchema,
    JobListItemResponseSchema,
    JobResponseSchema,
    JobSyncRequestSchema,
    PresignedUrlResponseItem,
    PresignedUrlsRequest,
    PresignedUrlsResponse,
)
from services.inspection_presigned import InspectionPresignedService
from services.job import JobService

logger = logging.getLogger(__name__)

job_router = APIRouter()


def get_inspection_presigned_service() -> InspectionPresignedService:
    """Dependency for inspection bucket presigned URL service (no DB)."""
    return InspectionPresignedService()


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


@job_router.patch(
    path='/{job_id}/assign_inspector',
    summary='Assign inspector to job',
    dependencies=[Depends(get_current_user)],
)
async def assign_inspector_to_job(
    job_id: int,
    inspector_data: AssignInspectorRequestSchema,
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> JobResponseSchema:
    job = await job_service.assign_inspector(
        job_id=job_id,
        inspector_data=inspector_data,
    )
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


@job_router.post(
    path='/{job_id}/upload-urls',
    summary='Get presigned URLs for direct upload to inspection S3',
    description=(
        'Returns a batch of presigned PUT URLs for uploading inspection assets '
        '(photos, floor plans, samples, documents, signatures) directly to the '
        'private inspection bucket. Call this before /sync; then send the '
        'returned s3_key values in the sync payload.'
    ),
    response_model=PresignedUrlsResponse,
    dependencies=[Depends(get_current_user)],
)
async def get_presigned_upload_urls(
    job_id: int,
    payload: PresignedUrlsRequest,
    presigned_service: Annotated[
        InspectionPresignedService, Depends(get_inspection_presigned_service)
    ],
) -> PresignedUrlsResponse:
    items = []
    for item in payload.files:
        s3_key = InspectionPresignedService.build_s3_key(
            job_id=job_id,
            file_type=item.file_type,
            file_id=item.file_id,
            extension=item.extension,
        )
        upload_url = presigned_service.generate_presigned_put_url(s3_key)
        if upload_url is None:
            raise HTTPException(
                status_code=500,
                detail=f'Failed to generate upload URL for file_id={item.file_id}',
            )
        items.append(
            PresignedUrlResponseItem(
                file_id=item.file_id,
                s3_key=s3_key,
                upload_url=upload_url,
            )
        )
    return PresignedUrlsResponse(urls=items)


@job_router.post(
    path='/{job_id}/sync',
    summary='Sync offline inspection data for a job',
    dependencies=[Depends(get_current_user)],
)
async def sync_offline_inspection(
    job_id: int,
    payload: JobSyncRequestSchema,
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> JobResponseSchema:
    job = await job_service.sync_offline_inspection(
        job_id=job_id,
        payload=payload,
    )
    return JobResponseSchema.model_validate(job)


@job_router.get(
    path='/by-project/{project_id}',
    summary='Get jobs by project id',
    dependencies=[Depends(get_current_user)],
)
async def get_jobs_by_project(
    project_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[JobListFiltersSchema, Depends()],
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> PaginatedResponse[JobListItemResponseSchema]:
    items, total = await job_service.get_jobs_by_project(
        project_id=project_id,
        pagination=pagination,
        filters=filters,
    )
    pages = (total + pagination.size - 1) // pagination.size
    return PaginatedResponse(
        items=[
            JobListItemResponseSchema.model_validate(item) for item in items
        ],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )


@job_router.get(
    path='/by-inspector/{inspector_id}',
    summary='Get jobs by inspector id',
    dependencies=[Depends(get_current_user)],
)
async def get_jobs_by_inspector(
    inspector_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    job_service: Annotated[JobService, Depends(get_service(JobService))],
) -> PaginatedResponse[JobListItemResponseSchema]:
    items, total = await job_service.get_jobs_by_inspector(
        inspector_id=inspector_id,
        pagination=pagination,
    )
    pages = (total + pagination.size - 1) // pagination.size
    return PaginatedResponse(
        items=[
            JobListItemResponseSchema.model_validate(item) for item in items
        ],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )

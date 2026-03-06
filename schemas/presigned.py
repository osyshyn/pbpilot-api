"""Schemas for inspection asset presigned URL requests and responses.

Used by the mobile app to obtain direct-upload (PUT) URLs to the private
inspection S3 bucket before calling the job sync endpoint with s3_key references.
"""

from enum import Enum

from pydantic import BaseModel, Field


class InspectionFileTypeEnum(str, Enum):
    """Type of file for inspection storage path.

    Maps to S3 folder structure:
    - photos: jobs/{job_id}/photos/{file_id}.{ext}
    - floor_plan: jobs/{job_id}/floor_plans/{file_id}.{ext}
    - sample: jobs/{job_id}/samples/{file_id}.{ext}
    - document: jobs/{job_id}/documents/{file_id}.{ext}
    - signature: jobs/{job_id}/signatures/{file_id}.{ext}
    """

    PHOTO = 'photo'
    FLOOR_PLAN = 'floor_plan'
    SAMPLE = 'sample'
    DOCUMENT = 'document'
    SIGNATURE = 'signature'


class PresignedUrlRequestItem(BaseModel):
    """Single file descriptor for presigned URL generation."""

    file_id: str = Field(..., description='UUID of the file from the mobile app')
    file_type: InspectionFileTypeEnum
    extension: str = Field(default='jpg', description='File extension without dot (jpg, png, pdf)')


class PresignedUrlsRequest(BaseModel):
    """Request body: list of files to get upload URLs for."""

    files: list[PresignedUrlRequestItem]


class PresignedUrlResponseItem(BaseModel):
    """Single presigned URL response item."""

    file_id: str
    s3_key: str = Field(..., description='S3 key to send later in sync payload')
    upload_url: str = Field(..., description='Presigned PUT URL for direct upload to S3')


class PresignedUrlsResponse(BaseModel):
    """Response: list of presigned PUT URLs and s3_keys."""

    urls: list[PresignedUrlResponseItem]

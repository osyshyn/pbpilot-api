"""Service for generating presigned URLs for the private inspection S3 bucket.

Uses AWS_INSPECTION_BUCKET_NAME (e.g. pbpilot-inspection-assets). Keys follow:
- jobs/{job_id}/photos/{file_id}.{ext}
- jobs/{job_id}/floor_plans/{file_id}.{ext}
- jobs/{job_id}/samples/{file_id}.{ext}
- jobs/{job_id}/documents/{file_id}.{ext}
- jobs/{job_id}/signatures/{file_id}.{ext}
"""

import logging
from typing import Any

from botocore.exceptions import ClientError

from config.settings import Settings
from schemas.presigned import InspectionFileTypeEnum

from services.aws.base import AWSActions

logger = logging.getLogger(__name__)

settings = Settings.load()

_INSPECTION_SUBFOLDER: dict[InspectionFileTypeEnum, str] = {
    InspectionFileTypeEnum.PHOTO: 'photos',
    InspectionFileTypeEnum.FLOOR_PLAN: 'floor_plans',
    InspectionFileTypeEnum.SAMPLE: 'samples',
    InspectionFileTypeEnum.DOCUMENT: 'documents',
    InspectionFileTypeEnum.SIGNATURE: 'signatures',
}

_EXTENSION_TO_CONTENT_TYPE: dict[str, str] = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}


def _normalize_extension(ext: str) -> str:
    """Return extension without leading dot, lowercase."""
    return ext.lstrip('.').lower() if ext else 'jpg'


class InspectionPresignedService(AWSActions):
    """Generates presigned PUT/GET URLs for the inspection assets bucket."""

    DEFAULT_PUT_EXPIRATION = 900   # 15 minutes
    DEFAULT_GET_EXPIRATION = 3600  # 1 hour

    def __init__(self) -> None:
        super().__init__()
        self._s3_client = self.get_client(service_name='s3', resource=False)
        self._bucket_name = settings.aws_settings.INSPECTION_BUCKET_NAME

    @staticmethod
    def build_s3_key(
        job_id: int,
        file_type: InspectionFileTypeEnum,
        file_id: str,
        extension: str,
    ) -> str:
        """Build S3 key for inspection asset (naming convention).

        Args:
            job_id: Job id.
            file_type: Type of file (photo, floor_plan, etc.).
            file_id: UUID of the file from the client.
            extension: File extension without dot (e.g. jpg, png, pdf).

        Returns:
            S3 key, e.g. jobs/22/photos/abc-123.jpg
        """
        ext = _normalize_extension(extension)
        folder = _INSPECTION_SUBFOLDER[file_type]
        return f'jobs/{job_id}/{folder}/{file_id}.{ext}'

    def _content_type_for_extension(self, extension: str) -> str:
        return _EXTENSION_TO_CONTENT_TYPE.get(
            _normalize_extension(extension), 'application/octet-stream'
        )

    def generate_presigned_put_url(
        self,
        s3_key: str,
        *,
        content_type: str | None = None,
        expiration: int = DEFAULT_PUT_EXPIRATION,
    ) -> str | None:
        """Generate presigned URL for direct upload (PUT) from mobile to S3.

        Args:
            s3_key: Full S3 object key.
            content_type: MIME type for the upload (optional; derived from key if not set).
            expiration: URL validity in seconds.

        Returns:
            Presigned URL string, or None on client error.
        """
        if not content_type:
            ext = s3_key.split('.')[-1] if '.' in s3_key else 'jpg'
            content_type = self._content_type_for_extension(ext)
        params: dict[str, Any] = {
            'Bucket': self._bucket_name,
            'Key': s3_key,
            'ContentType': content_type,
        }
        try:
            return self._s3_client.generate_presigned_url(
                'put_object',
                Params=params,
                ExpiresIn=expiration,
            )
        except ClientError as e:
            logger.exception('Failed to generate presigned PUT URL: %s', e)
            return None

    def generate_presigned_get_url(
        self,
        s3_key: str,
        *,
        expiration: int = DEFAULT_GET_EXPIRATION,
    ) -> str | None:
        """Generate presigned URL for reading a private object (e.g. in admin or app).

        Args:
            s3_key: Full S3 object key.
            expiration: URL validity in seconds.

        Returns:
            Presigned URL string, or None on client error.
        """
        try:
            return self._s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket_name, 'Key': s3_key},
                ExpiresIn=expiration,
            )
        except ClientError as e:
            logger.exception('Failed to generate presigned GET URL: %s', e)
            return None

from fastapi import HTTPException


class JobException(HTTPException):
    """Base exception for all job-related errors."""


class JobNotFoundException(JobException):
    """Raised when job with given id is not found."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Job was not found by given id.',
        )


class JobSyncNotAllowedForTypeException(JobException):
    """Raised when sync is attempted for a job type without inspection data."""

    def __init__(self, inspection_type: str) -> None:
        super().__init__(
            status_code=400,
            detail=(
                'Sync is not allowed for jobs with '
                f'inspection_type={inspection_type}.'
            ),
        )


class JobSyncInspectionTypeMismatchException(JobException):
    """Raised when payload inspection_type does not match the job's type."""

    def __init__(self, job_id: int, db_type: str, payload_type: str) -> None:
        super().__init__(
            status_code=422,
            detail=(
                f'Inspection type mismatch for job {job_id}: '
                f'job has {db_type}, payload has {payload_type}. '
                'Use the same inspection_type as the job.'
            ),
        )

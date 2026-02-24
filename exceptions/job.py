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

from fastapi import HTTPException


class ProjectException(HTTPException):
    """Base exception for all project-related errors."""


class ProjectNotFoundException(ProjectException):
    """Raised when project with given id is not found."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Project was not found by given id.',
        )

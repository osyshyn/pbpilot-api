from fastapi import HTTPException


class CompanyException(HTTPException):
    """Base exception for all company-related errors."""


class CompanyAlreadyExistsNotFoundException(CompanyException):
    """Raised when project with given id is not found."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Company already exists with this name',
        )

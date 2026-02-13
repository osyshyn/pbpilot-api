from fastapi import HTTPException


class CompanyException(HTTPException):
    """Base exception for all company-related errors."""


class CompanyNotFoundException(CompanyException):
    """Raised when company with given id is not found."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Company was not found by given id.',
        )


class CompanyAlreadyExistsException(CompanyException):
    """Raised when company with this name already exists."""

    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            detail='Company already exists with this name',
        )

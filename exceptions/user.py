from fastapi import HTTPException


class UserException(HTTPException):
    """Base exception for all user-related errors."""


class EmailAlreadyRegisteredException(UserException):
    """Raised when email already registered."""

    def __init__(self) -> None:
        """Initialize EmailAlreadyRegisteredException with a default message."""
        super().__init__(
            status_code=409,
            detail=(
                'You are trying to create user with email'
                ' that already has been taken'
            ),
        )

class UserIsNotActiveException(UserException):
    """Raised when user is not active."""

    def __init__(self) -> None:
        """Initialize UserIsNotActiveException with a default message."""
        super().__init__(
            status_code=404,
            detail='User is not active.',
        )
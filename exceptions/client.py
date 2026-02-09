from fastapi import HTTPException


class ClientException(HTTPException):
    """Base exception for all client-related errors."""


class ClientEmailAlreadyRegisteredException(ClientException):
    """Raised when email already registered."""

    def __init__(self) -> None:
        """Initialize ClientEmailAlreadyRegisteredException with a default message."""
        super().__init__(
            status_code=409,
            detail=(
                'Client with this email already registered'
            ),
        )
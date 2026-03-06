from fastapi import HTTPException


class EquipmentException(HTTPException):
    """Base exception for equipment-related errors."""


class EquipmentNotFoundException(EquipmentException):
    """Raised when equipment with given id is not found."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Equipment was not found by given id.',
        )


class CertificateFileIndexOutOfRangeException(EquipmentException):
    """Raised when certificate file index is out of range."""

    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail='Certificate file index out of range',
        )

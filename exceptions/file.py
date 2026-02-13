from fastapi import HTTPException


class FileException(HTTPException):
    pass


class UnknownFiletypeException(FileException):
    def __init__(self, allowed_types: list[str] | None = None) -> None:
        detail = 'Unsupported file type'
        if allowed_types:
            detail = (
                f'File type not allowed. Allowed types: '
                f'{", ".join(allowed_types)}'
            )
        super().__init__(
            status_code=400,
            detail=detail,
        )


class IncorrectFileSizeException(FileException):
    def __init__(self, max_size_mb: int | None = None) -> None:
        detail = 'Incorrect file size'
        if max_size_mb:
            detail = (
                f'File size exceeds maximum allowed size of {max_size_mb} MB'
            )
        super().__init__(
            status_code=400,
            detail=detail,
        )

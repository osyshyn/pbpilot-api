from typing import Generic, TypeVar

from fastapi import Query
from pydantic import Field

from core.schemas import BaseModelSchema

T = TypeVar('T')


class PaginationParams:
    """Dependency for pagination parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description='Page number'),
        size: int = Query(20, ge=1, le=100, description='Page size'),
    ):
        self.page = page
        self.size = size


class PaginatedResponse(BaseModelSchema, Generic[T]):
    """Generic response schema for paginated lists."""

    items: list[T]
    total: int = Field(..., description='Total number of items')
    page: int = Field(..., description='Current page number')
    size: int = Field(..., description='Number of items per page')
    pages: int = Field(..., description='Total number of pages')

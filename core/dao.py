"""Base classes and utilities for data access objects."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    """Base class for Data Access Objects."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize a new BaseDAO instance.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.

        """
        self._session: AsyncSession = db_session

    async def paginate(
        self,
        query: Any,
        page: int,
        limit: int,
    ) -> tuple[list[Any], int]:
        """Paginate query results.

        Args:
            query: SQLAlchemy query.
            page: Page number.
            limit: Page size.

        Returns:
            tuple[list[Any], int]: List of items and total count.

        """
        total = await self._session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        if not total:
            return [], 0

        items = await self._session.scalars(
            query.limit(limit).offset((page - 1) * limit)
        )
        return items.all(), total

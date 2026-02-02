"""Base classes and utilities for data access objects."""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    """Base class for Data Access Objects."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize a new BaseDAO instance.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.

        """
        self._session: AsyncSession = db_session

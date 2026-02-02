"""Dependency injection helpers for FastAPI routes and services."""

from collections.abc import AsyncGenerator, Callable
from typing import Annotated, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import async_session_maker
from core.service import BaseService

Service = TypeVar('Service', bound=BaseService)
"""Type variable for service classes bound to BaseService."""


async def get_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency for getting database session.

    Creates and yields an async database session. The session is automatically
    closed after the request is processed.

    Yields:
        AsyncSession: SQLAlchemy async database session.

    """
    async with async_session_maker() as session:
        yield session


def get_service[Service](
    service_type: type[Service],
) -> Callable[[AsyncSession], Service]:
    """Create a FastAPI dependency factory for service classes.

    This function creates a dependency injection function for FastAPI that
    instantiates a service class with a database session.

    Args:
        service_type: The service class type to instantiate.

    Returns:
        Callable that takes an AsyncSession and returns a Service instance.

    Example:
        ```python
        @router.get('/endpoint')
        async def endpoint(
            service: Annotated[ProjectsService,
             Depends(get_service(ProjectsService))]
        ):
            # service is automatically instantiated with db session
        ```

    """

    def _get_service(
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> Service:
        return service_type(db_session=db)  # type: ignore

    return _get_service

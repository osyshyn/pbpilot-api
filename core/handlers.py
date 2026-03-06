import logging
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from fastapi import HTTPException, status

T = TypeVar('T')

logger = logging.getLogger(__name__)


def exception_handler(  # noqa: UP047
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """Decorator for handling exceptions in async endpoints.

    Catches all exceptions except HTTPException and converts them
    to HTTP 500 Internal Server Error responses.

    Args:
        func: Async function to wrap.

    Returns:
        Wrapped function with exception handling.

    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            ) from e

    return wrapper


def timing_handler(  # noqa: UP047
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """Decorator for measuring execution time of async endpoints.

    Logs the execution time of the function in seconds with precision.
    Useful for monitoring performance, especially for AI processing endpoints.

    Args:
        func: Async function to wrap.

    Returns:
        Wrapped function with timing measurement.

    Example:
        ```python
        @timing_handler
        @exception_handler
        async def my_endpoint():
            # ... function code
        ```

    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            logger.info(
                'Function %s executed in %.3f seconds',
                func.__name__,
                elapsed_time,
            )
        except Exception:
            elapsed_time = time.perf_counter() - start_time
            logger.warning(
                'Function %s failed after %.3f seconds',
                func.__name__,
                elapsed_time,
            )
            raise
        else:
            return result

    return wrapper

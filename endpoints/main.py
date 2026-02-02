"""Main API endpoints for health checks and system status."""

from fastapi import APIRouter

from schemas.main import HealthCheckResponseSchema

main_router = APIRouter()
"""Router for main/health check endpoints."""


@main_router.get('/', response_model=HealthCheckResponseSchema)
async def health_check() -> HealthCheckResponseSchema:
    """Health check endpoint.

    Returns the current health status of the API.
    Used for monitoring, health checks, and deployment verification.

    Returns:
        HealthCheckResponseSchema: Response containing status 'ok'.

    """
    return HealthCheckResponseSchema()

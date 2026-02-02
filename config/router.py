"""Router initialization and configuration."""

from fastapi import APIRouter

from config.settings import Settings
from endpoints import (
    main_router, auth_router,
)

settings = Settings.load()


def initialize_routers() -> APIRouter:
    """Initialize and configure all API routers.

    Creates the main API router with version prefix and includes
    all sub-routers (main, project, contact, seo) with their prefixes and tags.

    Returns:
        APIRouter: Configured main API router with all endpoints included.

    """
    main_api_router = APIRouter(prefix=f'/api/{settings.API_VERSION}')
    main_api_router.include_router(main_router, prefix='/health', tags=['main'])
    main_api_router.include_router(auth_router, prefix='/auth', tags=['auth'])


    return main_api_router

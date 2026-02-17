"""Router initialization and configuration."""

import logging

from fastapi import APIRouter, FastAPI
from sqladmin import Admin

from admins import ADMIN_VIEWS
from config.database import engine
from config.settings import Settings
from endpoints import (
    auth_router,
    company_router,
    debug_router,
    main_router,
    pricing_plan_router,
    project_router,
    user_router, admin_router,
)
from endpoints.client import client_router

logger = logging.getLogger(__name__)
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
    main_api_router.include_router(user_router, prefix='/user')
    main_api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
    main_api_router.include_router(
        pricing_plan_router, prefix='/pricing_plan', tags=['pricing_plan']
    )
    main_api_router.include_router(
        client_router, prefix='/client', tags=['client']
    )
    main_api_router.include_router(
        project_router, prefix='/project', tags=['project']
    )
    main_api_router.include_router(
        company_router, prefix='/company', tags=['company']
    )
    main_api_router.include_router(
        admin_router, prefix='/admin', tags=['admin']
    )
    if settings.ENV in {'dev', 'local'}:
        main_api_router.include_router(
            debug_router, prefix='/debug', tags=['debug']
        )

    return main_api_router


def initialize_admin_panel(app: FastAPI) -> None:
    """Initialize an admin panel for the application."""
    if settings.ENV in {'dev', 'local'}:
        logger.info('Initializing admin panel: %s', ADMIN_VIEWS)
        admin = Admin(app=app, engine=engine)
        for view_name in ADMIN_VIEWS:
            admin.add_view(view_name)
    else:
        logger.info(
            'Settings is not local or dev, skipping admin panel initialization.'
        )

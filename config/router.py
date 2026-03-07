"""Router initialization and configuration."""

import logging

from fastapi import APIRouter, FastAPI
from sqladmin import Admin

from admins import ADMIN_VIEWS
from config.database import engine
from config.settings import Settings
from core import AdminAuth
from endpoints import (
    admin_router,
    auth_router,
    company_router,
    debug_router,
    equipment_router,
    inspector_router,
    job_router,
    lead_paint_router,
    main_router,
    pricing_plan_router,
    project_router,
    settings_router,
    user_router,
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
    main_api_router.include_router(
        inspector_router, prefix='/inspector', tags=['inspector']
    )
    main_api_router.include_router(
        equipment_router, prefix='/equipment', tags=['equipment']
    )
    main_api_router.include_router(job_router, prefix='/job', tags=['job'])
    main_api_router.include_router(
        lead_paint_router, prefix='/lead-paint', tags=['lead-paint']
    )
    main_api_router.include_router(
        settings_router, prefix='/settings', tags=['settings']
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
        authentication_backend = AdminAuth(
            secret_key="da01100e28c9943d3da853addc43defcf252756d43f1eb8663e9a939364a73e2"
        )
        admin = Admin(
            app=app,
            engine=engine,
            base_url="/admin",
            authentication_backend=authentication_backend,
        )
        for view_name in ADMIN_VIEWS:
            admin.add_view(view_name)
    else:
        logger.info(
            'Settings is not local or dev, skipping admin panel initialization.'
        )

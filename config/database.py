"""Database configuration and connection setup.

This module initializes SQLAlchemy async engine and session factory
for database operations.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import Settings

settings = Settings.load()


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class.

    This class serves as the base class for all SQLAlchemy
    models in the application.
    It provides the basic functionality and configuration
    for model classes to interact
    with the database using SQLAlchemy's declarative mapping system.

    All database models should inherit from this class to ensure consistent
    behavior and proper database integration.
    """


engine = create_async_engine(
    settings.database_settings.url(),
    echo=settings.DEBUG if settings.DEBUG else False,
    pool_pre_ping=True,
)
"""SQLAlchemy async engine for database connections.

Configured with:
- Database URL from settings
- Echo mode enabled in DEBUG mode (logs SQL queries)
- Pool pre-ping enabled (verifies connections before use)
"""

async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
"""Async session factory for creating database sessions.

Sessions created from this factory:
- Use AsyncSession class for async operations
- Do not expire objects on commit (expire_on_commit=False)
- Are bound to the configured engine
"""

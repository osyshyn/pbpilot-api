"""Application settings and configuration management.

This module provides Pydantic-based settings classes for managing
application configuration from environment variables and .env files.
"""

import os
from functools import cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
"""Base directory of the project."""

env_mode = os.getenv('ENV', 'local')
"""Current environment mode (dev, prod, etc.)."""

match env_mode:
    case 'prod':
        env_file = BASE_DIR / '.env.prod'
    case 'dev':
        env_file = BASE_DIR / '.env.dev'
    case 'local':
        env_file = BASE_DIR / '.env.local'
"""Path to environment-specific .env file."""


class TokenSettings(BaseSettings):
    """Settings for JWT token generation and validation.

    All settings are prefixed with 'TOKEN_' in environment variables.

    Attributes:
        SECRET_KEY: Secret key for signing JWT tokens.
        ALGORITHM: Algorithm used for token signing (default: HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes.
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time in days.

    """

    model_config = SettingsConfigDict(
        env_prefix='TOKEN_', env_file=env_file, extra='ignore'
    )

    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30


class DatabaseSettings(BaseSettings):
    """Settings for database connection.

    All settings are prefixed with 'DB_' in environment variables.
    Supports both full URL and individual connection parameters.

    Attributes:
        URL: Full database URL (optional, takes precedence if provided).
        USER: Database username.
        PASSWORD: Database password.
        HOST: Database host.
        PORT: Database port.
        DB_NAME: Database name.
        SSL: Whether to use SSL connection.

    """

    model_config = SettingsConfigDict(
        env_prefix='DB_', env_file=env_file, extra='ignore'
    )

    URL: str | None = None

    USER: str | None = None
    PASSWORD: str | None = None
    HOST: str | None = None
    PORT: str | None = None
    DB_NAME: str | None = None
    SSL: bool | None = None

    def _ssl(self) -> str:
        """Get SSL query parameter for database URL.

        Returns:
            SSL query parameter string if SSL is enabled, or empty string.

        """
        return '?sslmode=require' if self.SSL else ''

    def url(self) -> str:
        """Generate database connection URL.

        If URL is provided directly, returns it. Otherwise, constructs
        the URL from individual connection parameters.

        Returns:
            Database connection URL string.

        """
        if self.URL:
            return self.URL
        return f'postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB_NAME}{self._ssl}'


class LoggingSettings(BaseSettings):
    """Settings for application logging.

    All settings are prefixed with 'LOGGING_' in environment variables.

    """

    model_config = SettingsConfigDict(
        env_prefix='LOGGING_', env_file=env_file, extra='ignore'
    )


class Settings(BaseSettings):
    """Main application settings class.

    Aggregates all nested settings classes and provides top-level
    application configuration. Settings are loaded from environment
    variables and .env files based on the ENV variable.

    Attributes:
        API_TITLE: Title of the API (used in OpenAPI docs).
        API_VERSION: API version string (used in URL prefixes).
        ENV: Current environment (dev, prod, etc.).
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR).
        DEBUG: Whether debug mode is enabled.
        token_settings: Nested token configuration.
        database_settings: Nested database configuration.
        logging_settings: Nested logging configuration.
        aws_settings: Nested AWS configuration.
        email_settings: Nested email configuration.

    """

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding='utf-8',
        extra='ignore',
    )
    # Api version
    API_TITLE: str = 'Pbpilot API'
    API_VERSION: str = 'v1'

    # Log level
    ENV: str = env_mode
    LOG_LEVEL: str = 'INFO'
    DEBUG: bool = False

    # Expiration reminder settings
    REMINDER_DAYS: list[int] = [30, 15, 7]
    """Days before expiration to send reminders."""

    # Nested settings
    token_settings: TokenSettings = Field(default_factory=TokenSettings)
    database_settings: DatabaseSettings = Field(
        default_factory=DatabaseSettings
    )
    logging_settings: LoggingSettings = Field(default_factory=LoggingSettings)

    @classmethod
    @cache
    def load(cls) -> 'Settings':
        """Load and return a cached Settings instance.

        Uses functools.cache to ensure only one instance is created
        per process, improving performance and consistency.

        Returns:
            Settings: Cached Settings instance.

        """
        return cls()

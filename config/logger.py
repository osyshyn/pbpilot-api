"""Logging configuration for the application."""

import logging
import sys

from config.settings import Settings

LOG_FORMAT_DEBUG = '%(levelname)s:     %(message)s : %(funcName)s'
"""Log format string for debug mode with function name."""

LOG_FORMAT_CLOUDWATCH = (
    '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
)
"""Log format string for CloudWatch with timestamp, level, module, and message."""  # noqa: E501


def configure_logging() -> None:
    """Configure application-wide logging.

    Sets up Python logging with the configured log level and format
    from application settings. Should be called at application startup.

    Logs are sent to stdout/stderr and can be collected by logging
    services (e.g., CloudWatch, Docker logs, etc.).

    """
    settings = Settings.load()

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create console handler (stdout) - captured by Docker/logging services
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)

    # Use CloudWatch-friendly format with timestamp
    formatter = logging.Formatter(
        LOG_FORMAT_CLOUDWATCH, datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Ensure logs are flushed immediately
    console_handler.flush()

    # Suppress noisy third-party loggers
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

from pydantic import BaseModel

_DEFAULT_STATUS: str = 'ok'
"""Default status value for health check responses."""


class HealthCheckResponseSchema(BaseModel):
    """Response schema for health check endpoint.

    Attributes:
        status: Health status of the API (default: 'ok').

    """

    status: str = _DEFAULT_STATUS

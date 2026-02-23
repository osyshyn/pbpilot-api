from typing import Any

import boto3

from config.settings import Settings

settings = Settings.load()


class AWSActions:
    """Base class for AWS service interactions.

    Provides boto3 session management and client/resource creation.
    Handles different authentication methods for dev and prod environments.

    Attributes:
        session: Boto3 session instance for AWS service access.

    """

    def __init__(self) -> None:
        """Initialize AWS session based on environment.

        In development environment, uses access key and secret key.
        In production, uses IAM role credentials (no explicit keys needed).

        """
        if settings.ENV == 'dev':
            self.session = boto3.Session(
                aws_access_key_id=settings.aws_settings.ACCESS_KEY_ID,
                aws_secret_access_key=settings.aws_settings.SECRET_ACCESS_KEY,
                region_name=settings.aws_settings.REGION,
            )
        else:
            self.session = boto3.Session(
                region_name=settings.aws_settings.REGION
            )

    def _get(self, service_name: str, *, resource: bool = False) -> Any:
        """Get AWS service client or resource.

        Args:
            service_name: Name of the AWS service (e.g., 's3', 'dynamodb').
            resource: If True, returns a resource object; or a client.

        Returns:
            Boto3 client or resource object for the specified service.

        """
        if resource:
            return self.session.resource(  # type: ignore[call-overload]
                service_name,
                endpoint_url=f'https://s3.{settings.aws_settings.REGION}.amazonaws.com',
            )

        return self.session.client(  # type: ignore[call-overload]
            service_name,
            endpoint_url=f'https://s3.{settings.aws_settings.REGION}.amazonaws.com',
        )

    def get_client(self, service_name: str, *, resource: bool = False) -> Any:
        """Get AWS service client or resource (public method).

        Args:
            service_name: Name of the AWS service (e.g., 's3', 'dynamodb').
            resource: If True, returns a resource object;
             otherwise returns a client.

        Returns:
            Boto3 client or resource object for the specified service.

        """
        return self._get(service_name, resource=resource)

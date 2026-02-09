from typing import Annotated

from pydantic import Field

from core import BaseModelSchema, BaseUpdateSchema


class _BaseClientSchema(BaseModelSchema):
    """Base client schema."""

    id: Annotated[
        int, Field(description='Unique identifier of the client', examples=[1])
    ]
    email: Annotated[
        str,
        Field(
            description='Email address of the client',
            examples=['john_doe@gmail.com'],
            min_length=3,
            max_length=128,
        ),
    ]
    phone_number: Annotated[
        str,
        Field(
            description='Phone number of the client',
            examples=['+12345678901'],
            min_length=3,
            max_length=128,
        ),
    ]
    business_address: Annotated[
        str,
        Field(
            description='Phone number of the client',
            examples=['Main Street'],
            min_length=3,
            max_length=128,
        ),
    ]
    full_name: Annotated[
        str,
        Field(
            description='Full name of the client',
            examples=['John Doe'],
        ),
    ]


class CreateClientRequestSchema(BaseModelSchema):
    """Schema for creating a new client."""

    name: Annotated[
        str,
        Field(
            description='First name of the client',
            examples=['John'],
            min_length=3,
            max_length=128,
        ),
    ]
    surname: Annotated[
        str,
        Field(
            description='Last name of the client',
            examples=['Doe'],
            min_length=3,
            max_length=128,
        ),
    ]
    email: Annotated[
        str,
        Field(
            description='Email address of the client',
            examples=['john_doe@gmail.com'],
            min_length=3,
            max_length=128,
        ),
    ]
    phone_number: Annotated[
        str,
        Field(
            description='Phone number of the client',
            examples=['+12345678901'],
            min_length=3,
            max_length=128,
        ),
    ]
    business_address: Annotated[
        str,
        Field(
            description='Phone number of the client',
            examples=['Main Street'],
            min_length=3,
            max_length=128,
        ),
    ]


class UpdateClientRequestSchema(BaseUpdateSchema):
    name: Annotated[
        str | None,
        Field(
            default=None,
            description='First name of the client',
            examples=['John'],
            min_length=3,
            max_length=128,
        ),
    ]
    surname: Annotated[
        str | None,
        Field(
            default=None,
            description='Last name of the client',
            examples=['Doe'],
            min_length=3,
            max_length=128,
        ),
    ]
    email: Annotated[
        str | None,
        Field(
            default=None,
            description='Email address of the client',
            examples=['john_doe_new_email@gmail.com'],
            min_length=3,
            max_length=128,
        ),
    ]
    phone_number: Annotated[
        str | None,
        Field(
            default=None,
            description='Phone number of the client',
            examples=['+12345678901'],
            min_length=3,
            max_length=128,
        ),
    ]
    business_address: Annotated[
        str | None,
        Field(
            default=None,
            description='Phone number of the client',
            examples=['Main Street'],
            min_length=3,
            max_length=128,
        ),
    ]


class ClientResponseSchema(_BaseClientSchema):
    """Schema representing a client."""

    active_projects: Annotated[
        int | None,
        Field(
            default=None,
            description='Number of active projects for the client',
            examples=[15],
        ),
    ]

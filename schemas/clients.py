from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core import BaseModelSchema
from models.user import UserRoleEnum


class _BaseClientSchema(BaseModelSchema):
    """Base client schema."""
    full_name: Annotated[
        str,
        Field(
            description='Full name of the client',
            examples=['John Doe', ],
        )
    ]


class CreateClientRequestSchema(BaseModelSchema):
    """Schema for creating a new client."""
    name: Annotated[
        str,
        Field(
            description='First name of the client',
            examples=['John', ],
            min_length=3,
            max_length=128,
        )
    ]
    surname: Annotated[
        str,
        Field(
            description='Last name of the client',
            examples=['Doe', ],
            min_length=3,
            max_length=128,
        )
    ]
    email: Annotated[
        str,
        Field(
            description='Email address of the client',
            examples=['john_doe@gmail.com', ],
            min_length=3,
            max_length=128,
        )
    ]
    phone_number: Annotated[
        str,
        Field(
            description='Phone number of the client',
            examples=['+12345678901', ],
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


class ClientResponseSchema(_BaseClientSchema):
    """Schema representing a client."""
    active_projects: Annotated[
        int | None,
        Field(
            default=None,
            description='Number of active projects for the client',
            examples=[15, ],
        )
    ]


class ClientListResponseSchema(BaseModelSchema):
    """Schema representing a list of clients."""
    items: list[ClientResponseSchema]

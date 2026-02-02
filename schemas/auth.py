from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from models.user import UserRoleEnum


class SignUpRequestSchema(BaseModel):
    email: Annotated[
        EmailStr,
        Field(
            min_length=3,
            max_length=254,
            pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            examples=[
                'admin@admin.com',
            ],
        ),
    ]
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            pattern=r'^[a-zA-Z]+$',
            examples=[
                'John',
            ],
        ),
    ]
    surname: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            pattern=r'^[a-zA-Z]+$',
            examples=[
                'Doe',
            ],
        ),
    ]
    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=20,
            pattern=r'^[A-Za-z\d!@#$%^&*]{8,}$',
            examples=['StrongP@ss9'],
        ),
    ]
    phone_number: Annotated[
        str,
        Field(
            min_length=1,
            max_length=32,
            description='Phone number (digits; +, spaces, dashes allowed)',
            examples=['+1 234 567 8901', '12345678900'],
        ),
    ]

class SignUpResponseSchema(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    role: UserRoleEnum
    is_active: bool
    phone: Annotated[
        str | None,
        Field(
            default=None,
            alias='phone_number',
            description='Phone number of the user',
        ),
    ] = None
    model_config = ConfigDict(from_attributes=True)
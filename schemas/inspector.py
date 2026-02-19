from datetime import datetime, date
from typing import Annotated, Self

from pydantic import Field, model_validator, EmailStr

from core import BaseModelSchema
from models.inspector import LicenseTypeEnum
from models.projects import BuildingTypeEnum, ProjectStatusEnum


class CreateInspectorRequestSchema(BaseModelSchema):
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
    phone_number: Annotated[
        str,
        Field(
            min_length=1,
            max_length=32,
            description='Phone number (digits; +, spaces, dashes allowed)',
            examples=['+1 234 567 8901', '12345678900'],
        ),
    ]
    license_number: Annotated[
        str,
        Field(
            min_length=1,
            max_length=32,
            description='LICE number',
            examples=["License #1"]
        )
    ]
    licence_type: LicenseTypeEnum
    issue_date: date
    expiration_date: date

class InspectorResponseSchema(BaseModelSchema):
    id: int
    full_name: str
    license_number: str
    expiration_date: date
    email: EmailStr
    phone_number: str

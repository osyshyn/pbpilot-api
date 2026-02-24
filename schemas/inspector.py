from datetime import date
from typing import Annotated, Self

from pydantic import EmailStr, Field

from core import BaseModelSchema
from models.inspector import LicenseTypeEnum
from fastapi import Form


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
            examples=['License #1'],
        ),
    ]
    licence_type: LicenseTypeEnum
    issue_date: date
    expiration_date: date

    @classmethod
    def from_form(cls, data: str = Form(...)) -> 'CreateInspectorRequestSchema':
        return cls.model_validate_json(data)

class InspectorResponseSchema(BaseModelSchema):
    id: int
    full_name: str
    license_number: str
    expiration_date: date
    email: EmailStr
    phone_number: str

from datetime import date
from typing import Annotated

from fastapi import Form
from pydantic import EmailStr, Field

from core import BaseModelSchema, BaseUpdateSchema
from models.inspector import LicenseTypeEnum


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


class UpdateInspectorRequestSchema(BaseUpdateSchema):
    """Schema for updating inspector (name, surname, email, phone)."""

    name: Annotated[
        str | None,
        Field(
            default=None,
            description='First name of the inspector',
            min_length=3,
            max_length=15,
            pattern=r'^[a-zA-Z]+$',
            examples=['John'],
        ),
    ]
    surname: Annotated[
        str | None,
        Field(
            default=None,
            description='Last name of the inspector',
            min_length=3,
            max_length=15,
            pattern=r'^[a-zA-Z]+$',
            examples=['Doe'],
        ),
    ]
    email: Annotated[
        EmailStr | None,
        Field(
            default=None,
            description='Email address of the inspector',
            min_length=3,
            max_length=254,
            examples=['inspector@example.com'],
        ),
    ]
    phone_number: Annotated[
        str | None,
        Field(
            default=None,
            description='Phone number of the inspector',
            min_length=1,
            max_length=32,
            examples=['+1 234 567 8901', '12345678900'],
        ),
    ]


class InspectorResponseSchema(BaseModelSchema):
    id: int
    full_name: str
    license_number: str
    expiration_date: date
    email: EmailStr
    phone_number: str


class _InspectorListWithAmountResponseSchema(BaseModelSchema):
    amount: Annotated[
        int,
        Field(
            description='Total amount',
            examples=[5],
        ),
    ]
    inspector_names: Annotated[
        list[str],
        Field(
            description='Full names of inspectors',
            examples=[['John Doe', 'Jane Smith']],
        ),
    ]


class _ReportsPendingResponseSchema(BaseModelSchema):
    amount: Annotated[
        int,
        Field(
            description='Number of pending reports',
            examples=[3],
        ),
    ]
    report_names: Annotated[
        list[str],
        Field(
            description='Names of pending reports',
            examples=[['Report 1', 'Report 2']],
        ),
    ]


class InspectorDashboardResponseSchema(BaseModelSchema):
    total_inspectors: _InspectorListWithAmountResponseSchema
    on_site_today: _InspectorListWithAmountResponseSchema
    available_now: _InspectorListWithAmountResponseSchema
    reports_pending: _ReportsPendingResponseSchema

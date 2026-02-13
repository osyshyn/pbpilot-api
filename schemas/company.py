from datetime import time
from typing import Annotated

from pydantic import Field

from core import BaseModelSchema


class CreateCompanyScheduleItemRequestSchema(BaseModelSchema):
    """One schedule entry: working hours for a weekday."""

    day_of_week: Annotated[
        int,
        Field(
            description='Day of week (0=Monday, 6=Sunday)',
            examples=[0],
            ge=0,
            le=6,
        ),
    ]
    start_time: Annotated[
        time | None,
        Field(
            default=None,
            description='Work start time for this day',
            examples=['09:00:00'],
        ),
    ]
    end_time: Annotated[
        time | None,
        Field(
            default=None,
            description='Work end time for this day',
            examples=['18:00:00'],
        ),
    ]



class CreateCompanyRequestSchema(BaseModelSchema):
    """Schema for creating a new company."""

    company_name: Annotated[
        str,
        Field(
            description='Name of the company',
            examples=['Acme Inc'],
            min_length=1,
            max_length=255,
        ),
    ]
    phone_number: Annotated[
        str | None,
        Field(
            default=None,
            description='Company phone number',
            examples=['+1234567890'],
            max_length=16,
        ),
    ]
    address: Annotated[
        str,
        Field(
            description='Business address',
            examples=['123 Main St, City'],
            min_length=1,
            max_length=255,
        ),
    ]
    timezone: Annotated[
        str,
        Field(
            description='Company timezone (e.g. Europe/London)',
            examples=['Europe/London'],
            min_length=1,
            max_length=50,
        ),
    ]
    schedule: Annotated[
        list[CreateCompanyScheduleItemRequestSchema],
        Field(
            description='Working hours per weekday (0=Mon .. 6=Sun)',
            examples=[
                [
                    {
                        'day_of_week': 0,
                        'start_time': '09:00',
                        'end_time': '18:00',
                        'is_day_off': False,
                        },
                    {
                        'day_of_week': 6,
                        'start_time': None,
                        'end_time': None,
                        'is_day_off': True,
                        },
                ],
            ],
        ),
    ]
    tax_state: Annotated[
        str,
        Field(
            description='State of the country',
            examples=['Washington'],
        ),
    ]
    tax_percentage: Annotated[
        float,
        Field(
            description='Tax percentage',
            examples=[0.15],
        ),
    ]


class CompanyScheduleItemResponseSchema(BaseModelSchema):
    """Schedule item in response."""

    id: int
    day_of_week: int
    start_time: time | None
    end_time: time | None
    is_day_off: bool


class CompanyResponseSchema(BaseModelSchema):
    """Schema for company in response."""

    id: int
    company_name: str
    phone_number: str | None
    address: str
    timezone: str
    logo_key: str | None
    schedule: list[CompanyScheduleItemResponseSchema] = []

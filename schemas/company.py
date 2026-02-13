from datetime import time
from typing import Annotated, Self

from pydantic import Field, model_validator

from core import BaseModelSchema


class CreateCompanyScheduleItemRequestSchema(BaseModelSchema):
    """One schedule entry: working hours for a weekday. Only working days."""

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
        time,
        Field(
            description='Work start time',
            examples=['09:00'],
        ),
    ]
    end_time: Annotated[
        time,
        Field(
            description='Work end time',
            examples=['18:00'],
        ),
    ]

    @model_validator(mode='after')
    def validate_working_hours(self) -> Self:
        if self.start_time >= self.end_time:
            raise ValueError('start_time must be before end_time')
        return self


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
    logo_key: Annotated[
        str | None,
        Field(
            default=None,
            description='S3 key for company logo',
            max_length=512,
        ),
    ]
    schedule: Annotated[
        list[CreateCompanyScheduleItemRequestSchema],
        Field(
            description='Working days only (0=Mon .. 6=Sun). Days not in list are off.',
            min_length=1,
            examples=[
                [
                    {
                        'day_of_week': 0,
                        'start_time': '09:00',
                        'end_time': '18:00',
                    },
                    {
                        'day_of_week': 1,
                        'start_time': '09:00',
                        'end_time': '18:00',
                    },
                    {
                        'day_of_week': 2,
                        'start_time': '09:00',
                        'end_time': '18:00',
                    },
                    {
                        'day_of_week': 3,
                        'start_time': '09:00',
                        'end_time': '18:00',
                    },
                    {
                        'day_of_week': 4,
                        'start_time': '09:00',
                        'end_time': '18:00',
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

    @model_validator(mode='after')
    def validate_schedule_unique_days(self) -> Self:
        days = [s.day_of_week for s in self.schedule]
        if len(days) != len(set(days)):
            raise ValueError(
                'Each day_of_week must appear at most once in schedule'
            )
        return self


class CompanyScheduleItemResponseSchema(BaseModelSchema):
    """Schedule item in response."""

    id: int
    day_of_week: int
    start_time: time
    end_time: time


class CompanyResponseSchema(BaseModelSchema):
    """Schema for company in response."""

    id: int
    company_name: str
    phone_number: str | None
    address: str
    timezone: str
    logo_key: str | None
    tax_state: str
    tax_percentage: float
    schedule: list[CompanyScheduleItemResponseSchema] = []

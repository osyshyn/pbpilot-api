from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from core import BaseModelSchema


class CreateUserByAdminRequestSchema(BaseModel):
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

class AssignFreeReportsRequestSchema(BaseModel):
    report_amount: Annotated[
        int,
        Field(
            ge=1,
            le=100,
            description='Number of free reports to assign',
            examples=[10],
        )
    ]

class AssignFreeReportsResponseSchema(BaseModelSchema):
    email: EmailStr
    free_reports_count: int
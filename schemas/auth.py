from typing import Annotated, Self

from pydantic import BaseModel, EmailStr, Field, model_validator

from core import BaseModelSchema
from models.user import UserRoleEnum, MarketingSourceEnum


class SignUpRequestSchema(BaseModel):
    """Schema representing user registration data."""

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
    marketing_source: Annotated[
        MarketingSourceEnum,
        Field(
            description='Source of the marketing campaign',
            examples=[
                MarketingSourceEnum.GOOGLE,
            ]
        ),
    ]
    marketing_source_details: Annotated[
        str | None,
        Field(
            default=None,
            description='Additional marketing source details',
            examples=['Google Ads'],
        ),
    ] = None

    @model_validator(mode='after')
    def validate_marketing_source(self) -> Self:
        source = self.marketing_source
        details = self.marketing_source_details
        if source == MarketingSourceEnum.OTHER and not details :
            raise ValueError("Please provide details for 'Other' source")
        if source != MarketingSourceEnum.OTHER and details:
            raise ValueError("Details are not required for other sources")
        return self



class SignUpResponseSchema(BaseModelSchema):
    """Schema representing user information after successful registration."""

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

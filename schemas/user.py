from typing import Annotated

from pydantic import Field, field_validator

from core import BaseModelSchema
from models.user import UserRoleEnum


class UserResponseSchema(BaseModelSchema):
    """User response schema."""

    id: int
    name: str
    surname: str
    email: str
    role: UserRoleEnum
    is_active: bool
    phone_number: Annotated[
        str | None,
        Field(
            default=None,
            alias='phone_number',
            description='Phone number of the user',
        ),
    ] = None
    is_onboarding_completed: Annotated[
        bool | None,
        Field(
            default=False,
            description='Is onboarding completed for the user',
            examples=[True],
        ),
    ] = False

    @field_validator('is_onboarding_completed', mode='before')
    def ensure_bool(cls, v: bool | None) -> bool:
        return bool(v)
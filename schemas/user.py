from typing import Annotated

from pydantic import Field

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

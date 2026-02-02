from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict

from models.user import UserRoleEnum


class UserResponseSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, ConfigDict, model_validator
from typing import Self

class BaseModelSchema(BaseModel):
    """Base schema for all models."""
    model_config = ConfigDict(from_attributes=True)


class BaseUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def check_at_least_one_field(self) -> Self:
        if not self.model_dump(exclude_unset=True):
            raise ValueError("At least one field must be provided for update")
        return self
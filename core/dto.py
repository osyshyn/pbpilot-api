from dataclasses import asdict, dataclass
import logging
from dataclasses import is_dataclass, fields
from typing import Any, Type, TypeVar, get_origin, get_args
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass(slots=True)
class BaseDTO:
    """Base Data Transfer Object (DTO) class.

    Provides a helper method to convert the dataclass to a dictionary.
    All DTOs should inherit from this class.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert the DTO instance to a dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of the DTO, where keys
            are field names and values are field values.

        """
        return asdict(self)


class DTOToSchemaConverter:
    """
    Universal, safe converter from dataclass DTOs to Pydantic schemas.

    Features:
    - Maps only matching field names
    - Recursively converts nested DTOs
    - Supports list fields
    - Optional strict mode
    - Structured logging
    """

    def __init__(self, strict: bool = False):
        """
        :param strict: If True, raises error when schema field
                       is missing in DTO.
        """
        self.strict = strict
        self.logger = logging.getLogger(self.__class__.__name__)

    def convert(self, dto: Any, schema_cls: Type[T]) -> T:
        if dto is None:
            self.logger.debug("Received None DTO, returning None.")
            return None

        if not is_dataclass(dto):
            raise TypeError(
                f"Expected dataclass instance, got {type(dto)}"
            )

        self.logger.debug(
            "Converting DTO %s to schema %s",
            dto.__class__.__name__,
            schema_cls.__name__,
        )

        schema_fields = schema_cls.model_fields
        dto_field_map = {
            f.name: getattr(dto, f.name)
            for f in fields(dto)
        }

        data = {}

        for field_name, schema_field in schema_fields.items():

            if field_name not in dto_field_map:
                if self.strict:
                    raise ValueError(
                        f"Field '{field_name}' missing in DTO "
                        f"{dto.__class__.__name__}"
                    )
                self.logger.debug(
                    "Skipping missing field '%s' in DTO %s",
                    field_name,
                    dto.__class__.__name__,
                )
                continue

            value = dto_field_map[field_name]

            if value is None:
                data[field_name] = None
                continue

            field_type = schema_field.annotation
            origin = get_origin(field_type)

            # Handle list fields
            if origin is list:
                item_type = get_args(field_type)[0]

                if value and is_dataclass(value[0]):
                    data[field_name] = [
                        self.convert(item, item_type)
                        for item in value
                    ]
                else:
                    data[field_name] = value

            # Handle nested DTO
            elif is_dataclass(value):
                data[field_name] = self.convert(value, field_type)

            # Primitive value
            else:
                data[field_name] = value

        self.logger.debug(
            "Successfully converted %s to %s",
            dto.__class__.__name__,
            schema_cls.__name__,
        )

        return schema_cls(**data)

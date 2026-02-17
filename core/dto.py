import logging
from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import (
    Any,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


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
    def __init__(self, strict: bool = False) -> None:
        self.strict = strict
        self.logger = logging.getLogger(self.__class__.__name__)

    def convert(self, dto: Any, schema_cls: type[T]) -> T | None:
        if dto is None:
            self.logger.debug('Received None DTO, returning None.')
            return None

        if not is_dataclass(dto):
            raise TypeError(f'Expected dataclass instance, got {type(dto)}')

        self.logger.debug(
            'Converting DTO %s to schema %s',
            dto.__class__.__name__,
            schema_cls.__name__,
        )

        schema_fields = schema_cls.model_fields
        dto_field_map = {f.name: getattr(dto, f.name) for f in fields(dto)}

        data: dict[str, Any] = {}

        for field_name, schema_field in schema_fields.items():
            if field_name not in dto_field_map:
                if self.strict:
                    raise ValueError(
                        f"Field '{field_name}' missing in DTO "
                        f'{dto.__class__.__name__}'
                    )
                continue

            value = dto_field_map[field_name]

            if value is None:
                data[field_name] = None
                continue

            field_type = schema_field.annotation
            resolved_type = self._resolve_optional(field_type)
            origin = get_origin(resolved_type)

            # ---- LIST HANDLING ----
            if origin is list:
                item_type = get_args(resolved_type)[0]

                if (
                    isinstance(value, list)
                    and value
                    and is_dataclass(value[0])
                    and isinstance(item_type, type)
                    and issubclass(item_type, BaseModel)
                ):
                    data[field_name] = [
                        self.convert(item, item_type) for item in value
                    ]
                else:
                    data[field_name] = value

            # ---- NESTED DTO ----
            elif (
                is_dataclass(value)
                and isinstance(resolved_type, type)
                and issubclass(resolved_type, BaseModel)
            ):
                data[field_name] = self.convert(value, resolved_type)

            # ---- PRIMITIVE ----
            else:
                data[field_name] = value

        self.logger.debug(
            'Successfully converted %s to %s',
            dto.__class__.__name__,
            schema_cls.__name__,
        )

        return schema_cls(**data)

    @staticmethod
    def _resolve_optional(field_type: Any) -> Any:
        """Resolves Optional[T] or Union[T, None] to T."""
        origin = get_origin(field_type)

        if origin is Union:
            args = [
                arg for arg in get_args(field_type) if arg is not type(None)
            ]
            if len(args) == 1:
                return args[0]

        return field_type

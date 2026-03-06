import logging
from dataclasses import MISSING
from dataclasses import fields as dataclass_fields
from typing import Any, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SchemaMapper:
    @staticmethod
    def to_dto(
        dto_class: type[T],
        schema: BaseModel,
        **extra: Any,
    ) -> T:
        schema_data = schema.model_dump()
        dto_fields = {f.name for f in dataclass_fields(dto_class)}  # type: ignore[arg-type]

        skipped_from_schema = {k for k in schema_data if k not in dto_fields}
        skipped_from_extra = {k for k in extra if k not in dto_fields}

        if skipped_from_schema:
            logger.debug(
                'SchemaMapper: fields present in schema but missing in DTO will be skipped. '
                'dto=%s schema=%s skipped_fields=%s',
                dto_class.__name__,
                schema.__class__.__name__,
                sorted(skipped_from_schema),
            )

        if skipped_from_extra:
            logger.warning(
                'SchemaMapper: extra fields not found in DTO will be skipped. '
                'dto=%s skipped_extra_fields=%s',
                dto_class.__name__,
                sorted(skipped_from_extra),
            )

        filtered = {k: v for k, v in schema_data.items() if k in dto_fields}
        filtered.update({k: v for k, v in extra.items() if k in dto_fields})

        missing_required = {
            f.name
            for f in dataclass_fields(dto_class)  # type: ignore[arg-type]
            if f.default is f.default_factory is MISSING
            and f.name not in filtered
        }

        if missing_required:
            logger.error(
                'SchemaMapper: required DTO fields are missing and will cause an error. '
                'dto=%s missing_fields=%s',
                dto_class.__name__,
                sorted(missing_required),
            )

        return dto_class(**filtered)

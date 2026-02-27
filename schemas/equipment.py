from datetime import date
from typing import Annotated
import json

from fastapi import Form
from pydantic import Field

from core import BaseModelSchema
from models.equipment import OperationModeEnum


class CreateEquipmentRequestSchema(BaseModelSchema):
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['XFR'],
        ),
    ]
    manufacturer: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['SciApps'],
        ),
    ]
    model: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['X-550'],
        ),
    ]
    serial_number: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['1234'],
        ),
    ]
    mode: OperationModeEnum
    date_of_radioactive_source: Annotated[
        date, Field(None, description='Date of radioactive source')
    ]

    @classmethod
    def from_form(
        cls, equipment_data: str = Form(...)
    ) -> 'CreateEquipmentRequestSchema':
        """Parse single equipment from form JSON."""
        return cls.model_validate_json(equipment_data)

    @classmethod
    def list_from_form(
        cls,
        equipment_data: str = Form(...),
    ) -> list['CreateEquipmentRequestSchema']:
        parsed = json.loads(equipment_data)
        if isinstance(parsed, list):
            return [cls.model_validate(item) for item in parsed]
        return [cls.model_validate(parsed)]


class EquipmentResponseSchema(BaseModelSchema):
    name: str
    manufacturer: str
    model: str
    serial_number: str
    mode: OperationModeEnum
    date_of_radioactive_source: date

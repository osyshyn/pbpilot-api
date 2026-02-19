from datetime import time, date
from typing import Annotated, Self

from pydantic import Field, model_validator

from core import BaseModelSchema
from models.equipment import OperationModeEnum


class CreateEquipmentRequestSchema(BaseModelSchema):
    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['XFR'],
        )
    ]
    manufacturer: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['SciApps'],
        )
    ]
    model: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['X-550'],
        )
    ]
    serial_number: Annotated[
        str,
        Field(
            min_length=3,
            max_length=15,
            examples=['1234'],
        )
    ]
    mode: OperationModeEnum
    date_of_radioactive_source: Annotated[
        date,
        Field(
            None,
            description='Date of radioactive source'
        )
    ]

class EquipmentResponseSchema(BaseModelSchema):
    name: str
    manufacturer: str
    model: str
    serial_number: str
    mode: OperationModeEnum
    date_of_radioactive_source: date
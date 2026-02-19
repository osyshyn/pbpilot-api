from dataclasses import dataclass
from datetime import date

from core.dto import BaseDTO
from models.equipment import OperationModeEnum


@dataclass(slots=True)
class CreateEquipmentDTO(BaseDTO):
    name: str
    manufacturer: str
    model: str
    serial_number: str
    mode: OperationModeEnum
    date_of_radioactive_source: date | None = None,
    training_certificate_key: str | None = None


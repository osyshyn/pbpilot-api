from dataclasses import dataclass
from datetime import date

from core.dto import BaseDTO
from models.inspector import LicenseTypeEnum


@dataclass(slots=True)
class CreateInspectorDTO(BaseDTO):
    name: str
    surname: str
    email: str
    license_number: str
    licence_type: LicenseTypeEnum
    issue_date: date
    expiration_date: date
    license_image_key: str
    phone_number: str | None = None







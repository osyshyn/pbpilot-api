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
    license_image_keys: list[str]
    phone_number: str | None = None


@dataclass(slots=True)
class TotalInspectorsDTO(BaseDTO):
    amount: int
    inspector_names: list[str]


@dataclass(slots=True)
class OnSiteTodayDTO(BaseDTO):
    amount: int
    inspector_names: list[str]


@dataclass(slots=True)
class AvailableNowDTO(BaseDTO):
    amount: int
    inspector_names: list[str]


@dataclass(slots=True)
class ReportsPendingDTO(BaseDTO):
    amount: int
    report_names: list[str]


@dataclass(slots=True)
class InspectorDashboardDTO(BaseDTO):
    total_inspectors: TotalInspectorsDTO
    on_site_today: OnSiteTodayDTO
    available_now: AvailableNowDTO
    reports_pending: ReportsPendingDTO

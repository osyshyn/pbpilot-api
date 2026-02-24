from dataclasses import dataclass
from datetime import datetime

from core.dto import BaseDTO
from models.jobs import InspectionTypeEnum
from models.projects import BuildingTypeEnum, ProjectStatusEnum


@dataclass(slots=True)
class JobInfoDTO(BaseDTO):
    job_type: InspectionTypeEnum
    owner_name: str
    property_manager: str | None
    owner_business_address: str
    owner_email: str
    owner_phone_number: str | None
    status: ProjectStatusEnum
    inspector: str | None
    created_at: datetime
    scheduled_time: datetime | None
    progress_percent: int


@dataclass(slots=True)
class JobPropertyDetailsDTO(BaseDTO):
    property_address: str
    structure_type: BuildingTypeEnum
    number_of_units: int
    inspection_date: datetime | None
    owner_lcc_name: str | None
    year_of_construction: int | None
    parcel_number: str | None
    rental_registration_number: str | None


@dataclass(slots=True)
class JobInspectionProgressDTO(BaseDTO):
    job_created: bool
    inspection_scheduled: bool
    inspection_completed: bool
    lab_results_received: bool
    invoice_sent_to_client: bool
    report_generated: bool
    report_sent_to_client: bool


@dataclass(slots=True)
class JobDetailsDTO(BaseDTO):
    job: JobInfoDTO
    property: JobPropertyDetailsDTO
    progress: JobInspectionProgressDTO
    notes: str | None


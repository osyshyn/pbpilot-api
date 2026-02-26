from dataclasses import dataclass
from datetime import datetime

from core.dto import BaseDTO


@dataclass(slots=True)
class OngoingProjectDTO(BaseDTO):
    amount: int = 0
    scheduled: int = 0
    need_scheduled: int = 0
    completed_this_week: int = 0


@dataclass(slots=True)
class NeedScheduledDTO(BaseDTO):
    project_names: list[str]
    amount: int = 0


@dataclass(slots=True)
class UnassignedJobsDTO(BaseDTO):
    project_names: list[str]
    amount: int = 0


@dataclass(slots=True)
class ReadyToFinalizeDTO(BaseDTO):
    project_names: list[str]
    amount: int = 0


@dataclass(slots=True)
class ProjectDashboardDTO(BaseDTO):
    ongoing_project: OngoingProjectDTO
    need_scheduling: NeedScheduledDTO
    unassigned_jobs: UnassignedJobsDTO
    ready_for_finalize: ReadyToFinalizeDTO


@dataclass(slots=True)
class ProjectInformationDTO(BaseDTO):
    project_name: str
    total_properties: int
    total_units: int
    created_date: datetime
    last_updated: datetime


@dataclass(slots=True)
class ProjectContactDetailsDTO(BaseDTO):
    client_fullname: str
    client_phone: str | None
    client_email: str


@dataclass(slots=True)
class ProjectLabResultDTO(BaseDTO):
    laboratory_name: str
    match_status: str
    status: str


@dataclass(slots=True)
class ProjectReportDTO(BaseDTO):
    report_name: str
    creation_date: datetime


@dataclass(slots=True)
class ProjectDetailsDTO(BaseDTO):
    project_information: ProjectInformationDTO
    contact_details: ProjectContactDetailsDTO
    lab_results: list[ProjectLabResultDTO]
    reports: list[ProjectReportDTO]

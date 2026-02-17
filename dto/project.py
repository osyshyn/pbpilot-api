from dataclasses import dataclass
from datetime import datetime as dt

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
    ongoing: OngoingProjectDTO
    need_schedule: NeedScheduledDTO
    unassigned: UnassignedJobsDTO
    ready_to_finalize: ReadyToFinalizeDTO
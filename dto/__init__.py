from .auth import AccessTokenDTO
from .equimpent import CreateEquipmentDTO
from .job import (
    JobDetailsDTO,
    JobInfoDTO,
    JobInspectionProgressDTO,
    JobPropertyDetailsDTO,
)
from .project import (
    NeedScheduledDTO,
    OngoingProjectDTO,
    ProjectDashboardDTO,
    ReadyToFinalizeDTO,
    UnassignedJobsDTO,
)
from .aws import UploadFileDTO
from .inspector import CreateInspectorDTO
__all__ = [
    'AccessTokenDTO',
    'CreateEquipmentDTO',
    'JobDetailsDTO',
    'JobInfoDTO',
    'JobInspectionProgressDTO',
    'JobPropertyDetailsDTO',
    'NeedScheduledDTO',
    'OngoingProjectDTO',
    'ProjectDashboardDTO',
    'ReadyToFinalizeDTO',
    'UnassignedJobsDTO',
    'UploadFileDTO',
    'CreateInspectorDTO',
]

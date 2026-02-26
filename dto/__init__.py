from .auth import AccessTokenDTO
from .aws import UploadFileDTO
from .equimpent import CreateEquipmentDTO
from .inspector import CreateInspectorDTO
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
    ProjectContactDetailsDTO,
    ProjectDetailsDTO,
    ProjectInformationDTO,
    ProjectLabResultDTO,
    ProjectReportDTO,
    ReadyToFinalizeDTO,
    UnassignedJobsDTO,
)

__all__ = [
    'AccessTokenDTO',
    'CreateEquipmentDTO',
    'CreateInspectorDTO',
    'JobDetailsDTO',
    'JobInfoDTO',
    'JobInspectionProgressDTO',
    'JobPropertyDetailsDTO',
    'NeedScheduledDTO',
    'OngoingProjectDTO',
    'ProjectDashboardDTO',
    'ProjectContactDetailsDTO',
    'ProjectDetailsDTO',
    'ProjectInformationDTO',
    'ProjectLabResultDTO',
    'ProjectReportDTO',
    'ReadyToFinalizeDTO',
    'UnassignedJobsDTO',
    'UploadFileDTO',
]

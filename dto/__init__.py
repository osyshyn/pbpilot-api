from .auth import AccessTokenDTO
from .aws import UploadFileDTO
from .equimpent import CreateEquipmentDTO
from .inspector import (
    AvailableNowDTO,
    CreateInspectorDTO,
    InspectorDashboardDTO,
    OnSiteTodayDTO,
    ReportsPendingDTO,
    TotalInspectorsDTO,
)
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
    'AvailableNowDTO',
    'CreateInspectorDTO',
    'InspectorDashboardDTO',
    'JobDetailsDTO',
    'JobInfoDTO',
    'JobInspectionProgressDTO',
    'JobPropertyDetailsDTO',
    'NeedScheduledDTO',
    'OngoingProjectDTO',
    'OnSiteTodayDTO',
    'ProjectDashboardDTO',
    'ProjectContactDetailsDTO',
    'ProjectDetailsDTO',
    'ProjectInformationDTO',
    'ProjectLabResultDTO',
    'ProjectReportDTO',
    'ReportsPendingDTO',
    'ReadyToFinalizeDTO',
    'TotalInspectorsDTO',
    'UnassignedJobsDTO',
    'UploadFileDTO',
]

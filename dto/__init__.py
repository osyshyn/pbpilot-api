from .auth import AccessTokenDTO
from .equimpent import CreateEquipmentDTO
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
    'NeedScheduledDTO',
    'OngoingProjectDTO',
    'ProjectDashboardDTO',
    'ReadyToFinalizeDTO',
    'UnassignedJobsDTO',
    'UploadFileDTO',
    'CreateInspectorDTO',
]

from .client import ClientAdmin
from .company import CompanyAdmin, CompanyScheduleAdmin
from .equipment import EquipmentAdmin
from .inspector import InspectorAdmin
from .job import JobAdmin
from .pricing_plan import PricingPlanAdmin
from .project import ProjectAdmin, ProjectPropertyAdmin, PropertyStructureAdmin
from .user import UserAdmin

ADMIN_VIEWS = [
    UserAdmin,
    ClientAdmin,
    CompanyAdmin,
    CompanyScheduleAdmin,
    InspectorAdmin,
    EquipmentAdmin,
    JobAdmin,
    ProjectAdmin,
    ProjectPropertyAdmin,
    PropertyStructureAdmin,
    PricingPlanAdmin,
]

__all__ = [
    'ADMIN_VIEWS',
    'BlacklistTokenAdmin',
    'ClientAdmin',
    'CompanyAdmin',
    'CompanyScheduleAdmin',
    'EquipmentAdmin',
    'InspectorAdmin',
    'JobAdmin',
    'PricingPlanAdmin',
    'ProjectAdmin',
    'ProjectPropertyAdmin',
    'PropertyStructureAdmin',
    'UserAdmin',
]

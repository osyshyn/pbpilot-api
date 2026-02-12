from .auth import auth_router
from .client import client_router
from .main import main_router
from .pricing_plan import pricing_plan_router
from .project import project_router
from .user import user_router
from .debug import debug_router
__all__ = [
    'auth_router',
    'client_router',
    'main_router',
    'pricing_plan_router',
    'project_router',
    'user_router',
]

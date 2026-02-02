from .main import main_router
from .auth import auth_router
from .user import user_router

__all__ = [
    'main_router',
    'auth_router',
    'user_router',
]

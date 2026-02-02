from .auth import auth_router
from .main import main_router
from .user import user_router

__all__ = [
    'auth_router',
    'main_router',
    'user_router',
]

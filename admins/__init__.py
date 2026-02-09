from .user import UserAdmin
from .client import ClientAdmin

ADMIN_VIEWS = [UserAdmin, ClientAdmin]

__all__ = ['UserAdmin', 'ClientAdmin', 'ADMIN_VIEWS']
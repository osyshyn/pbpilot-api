from .client import ClientAdmin
from .user import UserAdmin

ADMIN_VIEWS = [UserAdmin, ClientAdmin]

__all__ = ['ADMIN_VIEWS', 'ClientAdmin', 'UserAdmin']

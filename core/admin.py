from typing import Any, ClassVar
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

_ADMIN_USERNAME: str = "admin"
_ADMIN_PASSWORD: str = "0fBmZH89oCog"


class TimestampAdminMixin:
    """Mixin class for handling timestamp fields in the admin interface.

    This mixin provides basic configuration for handling
    created_at and updated_at timestamp fields in admin forms.
    It sets these fields as read-only and disabled
    to prevent manual modification of timestamps.

    Attributes:
        form_args: Class-level dictionary containing form field configurations
            for created_at and updated_at fields.

    """

    form_args: ClassVar[dict[str, Any]] = {
        'created_at': {'render_kw': {'readonly': True, 'disabled': True}},
        'updated_at': {'render_kw': {'readonly': True, 'disabled': True}},
    }


class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        if (
                form.get("username") == _ADMIN_USERNAME and
                form.get("password") == _ADMIN_PASSWORD
        ):
            request.session["admin_authenticated"] = True
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin_authenticated", False)

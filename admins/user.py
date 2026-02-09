from typing import ClassVar

from sqladmin import ModelView
from models import User
from core.admin import TimestampAdminMixin

class UserAdmin(TimestampAdminMixin, ModelView, model=User):

    column_list: ClassVar = [
        User.id,
        User.name,
        User.surname,
        User.email,
        User.phone_number,
        User.role,
        User.current_plan,
        User.billing_period,
    ]
    form_excluded_columns: ClassVar = [User.created_at, User.updated_at]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
        'balance': {'render_kw': {'readonly': True, 'disabled': True}},
    }

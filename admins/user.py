from typing import ClassVar

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter

from core.admin import TimestampAdminMixin
from models import User


class UserAdmin(TimestampAdminMixin, ModelView, model=User):
    name = 'User'
    name_plural = 'Users'
    icon = 'fa-solid fa-users'

    column_list: ClassVar = [
        User.id,
        User.name,
        User.surname,
        User.email,
        User.phone_number,
        User.role,
        User.is_onboarding_completed,
        User.current_plan,
        User.billing_period,
        User.free_reports_count,
        User.marketing_source,
        User.marketing_source_details,
        User.created_at,
        User.updated_at,
    ]
    column_searchable_list: ClassVar = [
        User.name,
        User.surname,
        User.email,
        User.phone_number,
    ]
    column_sortable_list: ClassVar = [
        User.id,
        User.name,
        User.surname,
        User.email,
        User.role,
        User.current_plan,
        User.billing_period,
        User.free_reports_count,
        User.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(User.role, title='Role'),
        AllUniqueStringValuesFilter(User.current_plan, title='Plan'),
        AllUniqueStringValuesFilter(User.billing_period, title='Billing Period'),
        BooleanFilter(User.is_onboarding_completed, title='Onboarding Completed'),
        AllUniqueStringValuesFilter(User.marketing_source, title='Marketing Source'),
    ]
    form_excluded_columns: ClassVar = [
        User.created_at,
        User.updated_at,
        User.deleted_at,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
        'password': {'render_kw': {'readonly': True, 'disabled': True}},
        'free_reports_count': {'render_kw': {'min': 0}},
    }

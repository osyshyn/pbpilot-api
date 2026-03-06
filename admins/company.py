from typing import ClassVar

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter

from core.admin import TimestampAdminMixin
from models import Company, CompanySchedule


class CompanyAdmin(TimestampAdminMixin, ModelView, model=Company):
    name = 'Company'
    name_plural = 'Companies'
    icon = 'fa-solid fa-building'

    column_list: ClassVar = [
        Company.id,
        Company.company_name,
        Company.phone_number,
        Company.address,
        Company.timezone,
        Company.tax_state,
        Company.tax_percentage,
        Company.logo_key,
        Company.created_at,
        Company.updated_at,
    ]
    column_searchable_list: ClassVar = [
        Company.company_name,
        Company.address,
        Company.tax_state,
    ]
    column_sortable_list: ClassVar = [
        Company.id,
        Company.company_name,
        Company.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(Company.tax_state, title='Tax State'),
        AllUniqueStringValuesFilter(Company.timezone, title='Timezone'),
    ]
    form_excluded_columns: ClassVar = [Company.created_at, Company.updated_at, Company.schedule]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }


class CompanyScheduleAdmin(TimestampAdminMixin, ModelView, model=CompanySchedule):
    name = 'Company Schedule'
    name_plural = 'Company Schedules'
    icon = 'fa-solid fa-calendar'

    column_list: ClassVar = [
        CompanySchedule.id,
        CompanySchedule.company_id,
        CompanySchedule.day_of_week,
        CompanySchedule.start_time,
        CompanySchedule.end_time,
    ]
    column_sortable_list: ClassVar = [
        CompanySchedule.id,
        CompanySchedule.company_id,
        CompanySchedule.day_of_week,
    ]
    form_excluded_columns: ClassVar = [CompanySchedule.company]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }

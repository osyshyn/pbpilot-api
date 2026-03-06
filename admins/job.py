from typing import ClassVar

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter

from core.admin import TimestampAdminMixin
from models import Job


class JobAdmin(TimestampAdminMixin, ModelView, model=Job):
    name = 'Job'
    name_plural = 'Jobs'
    icon = 'fa-solid fa-briefcase'

    column_list: ClassVar = [
        Job.id,
        Job.property_id,
        Job.inspector_id,
        Job.inspection_type,
        Job.status,
        Job.notes,
        Job.created_at,
        Job.updated_at,
    ]
    column_searchable_list: ClassVar = [
        Job.notes,
    ]
    column_sortable_list: ClassVar = [
        Job.id,
        Job.property_id,
        Job.inspector_id,
        Job.inspection_type,
        Job.status,
        Job.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(Job.status, title='Status'),
        AllUniqueStringValuesFilter(Job.inspection_type, title='Inspection Type'),
    ]
    form_excluded_columns: ClassVar = [
        Job.created_at,
        Job.updated_at,
        Job.deleted_at,
        Job.property,
        Job.inspector,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }

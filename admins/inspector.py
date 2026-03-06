from typing import ClassVar

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter

from core.admin import TimestampAdminMixin
from models import Inspector


class InspectorAdmin(TimestampAdminMixin, ModelView, model=Inspector):
    name = 'Inspector'
    name_plural = 'Inspectors'
    icon = 'fa-solid fa-user-tie'

    column_list: ClassVar = [
        Inspector.id,
        Inspector.name,
        Inspector.surname,
        Inspector.email,
        Inspector.phone_number,
        Inspector.license_number,
        Inspector.licence_type,
        Inspector.issue_date,
        Inspector.expiration_date,
        Inspector.created_at,
        Inspector.updated_at,
    ]
    column_searchable_list: ClassVar = [
        Inspector.name,
        Inspector.surname,
        Inspector.email,
        Inspector.license_number,
    ]
    column_sortable_list: ClassVar = [
        Inspector.id,
        Inspector.name,
        Inspector.surname,
        Inspector.email,
        Inspector.issue_date,
        Inspector.expiration_date,
        Inspector.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(Inspector.licence_type, title='Licence Type'),
    ]
    form_excluded_columns: ClassVar = [
        Inspector.created_at,
        Inspector.updated_at,
        Inspector.deleted_at,
        Inspector.equipments,
        Inspector.license_image_keys,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }

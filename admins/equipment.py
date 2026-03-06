from typing import ClassVar

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter

from core.admin import TimestampAdminMixin
from models import Equipment


class EquipmentAdmin(TimestampAdminMixin, ModelView, model=Equipment):
    name = 'Equipment'
    name_plural = 'Equipment'
    icon = 'fa-solid fa-toolbox'

    column_list: ClassVar = [
        Equipment.id,
        Equipment.inspector_id,
        Equipment.name,
        Equipment.manufacturer,
        Equipment.model,
        Equipment.serial_number,
        Equipment.mode,
        Equipment.date_of_radioactive_source,
        Equipment.created_at,
        Equipment.updated_at,
    ]
    column_searchable_list: ClassVar = [
        Equipment.name,
        Equipment.manufacturer,
        Equipment.model,
        Equipment.serial_number,
    ]
    column_sortable_list: ClassVar = [
        Equipment.id,
        Equipment.inspector_id,
        Equipment.name,
        Equipment.manufacturer,
        Equipment.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(Equipment.mode, title='Mode'),
    ]
    form_excluded_columns: ClassVar = [
        Equipment.created_at,
        Equipment.updated_at,
        Equipment.deleted_at,
        Equipment.inspector,
        Equipment.training_certificate_keys,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }

from typing import ClassVar

from sqladmin import ModelView

from core.admin import TimestampAdminMixin
from models import Client


class ClientAdmin(TimestampAdminMixin, ModelView, model=Client):
    name = 'Client'
    name_plural = 'Clients'
    icon = 'fa-solid fa-address-book'

    column_list: ClassVar = [
        Client.id,
        Client.name,
        Client.surname,
        Client.email,
        Client.phone_number,
        Client.business_address,
        Client.last_activity,
        Client.created_at,
        Client.updated_at,
    ]
    column_searchable_list: ClassVar = [
        Client.name,
        Client.surname,
        Client.email,
        Client.phone_number,
        Client.business_address,
    ]
    column_sortable_list: ClassVar = [
        Client.id,
        Client.name,
        Client.surname,
        Client.email,
        Client.last_activity,
        Client.created_at,
    ]
    form_excluded_columns: ClassVar = [
        Client.created_at,
        Client.updated_at,
        Client.deleted_at,
        Client.projects,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }

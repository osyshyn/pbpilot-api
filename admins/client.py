from typing import ClassVar

from sqladmin import ModelView

from core.admin import TimestampAdminMixin
from models import Client


class ClientAdmin(TimestampAdminMixin, ModelView, model=Client):
    column_list: ClassVar = [
        Client.id,
        Client.name,
        Client.surname,
        Client.email,
        Client.phone_number,
        Client.business_address,
    ]
    form_excluded_columns: ClassVar = [Client.created_at, Client.updated_at]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
        'balance': {'render_kw': {'readonly': True, 'disabled': True}},
    }

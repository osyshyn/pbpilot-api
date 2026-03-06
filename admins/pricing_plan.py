from typing import ClassVar

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter

from core.admin import TimestampAdminMixin
from models import PricingPlan


class PricingPlanAdmin(TimestampAdminMixin, ModelView, model=PricingPlan):
    name = 'Pricing Plan'
    name_plural = 'Pricing Plans'
    icon = 'fa-solid fa-tag'

    column_list: ClassVar = [
        PricingPlan.id,
        PricingPlan.plan,
        PricingPlan.period,
        PricingPlan.price,
        PricingPlan.currency,
        PricingPlan.created_at,
        PricingPlan.updated_at,
    ]
    column_sortable_list: ClassVar = [
        PricingPlan.id,
        PricingPlan.plan,
        PricingPlan.period,
        PricingPlan.price,
        PricingPlan.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(PricingPlan.plan, title='Plan'),
        AllUniqueStringValuesFilter(PricingPlan.period, title='Period'),
        AllUniqueStringValuesFilter(PricingPlan.currency, title='Currency'),
    ]
    form_excluded_columns: ClassVar = [PricingPlan.created_at, PricingPlan.updated_at]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }

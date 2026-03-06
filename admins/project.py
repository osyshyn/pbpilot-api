from typing import ClassVar

from sqladmin import ModelView
from sqladmin.filters import AllUniqueStringValuesFilter

from core.admin import TimestampAdminMixin
from models import Project, ProjectProperty, PropertyStructure


class ProjectAdmin(TimestampAdminMixin, ModelView, model=Project):
    name = 'Project'
    name_plural = 'Projects'
    icon = 'fa-solid fa-folder-open'

    column_list: ClassVar = [
        Project.id,
        Project.client_id,
        Project.project_name,
        Project.property_manager_name,
        Project.status,
        Project.created_at,
        Project.updated_at,
    ]
    column_searchable_list: ClassVar = [
        Project.project_name,
        Project.property_manager_name,
    ]
    column_sortable_list: ClassVar = [
        Project.id,
        Project.client_id,
        Project.project_name,
        Project.status,
        Project.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(Project.status, title='Status'),
    ]
    form_excluded_columns: ClassVar = [
        Project.created_at,
        Project.updated_at,
        Project.deleted_at,
        Project.client,
        Project.properties,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }


class ProjectPropertyAdmin(TimestampAdminMixin, ModelView, model=ProjectProperty):
    name = 'Project Property'
    name_plural = 'Project Properties'
    icon = 'fa-solid fa-house'

    column_list: ClassVar = [
        ProjectProperty.id,
        ProjectProperty.project_id,
        ProjectProperty.address,
        ProjectProperty.type,
        ProjectProperty.number_of_units,
        ProjectProperty.owner_lcc_name,
        ProjectProperty.year_of_construction,
        ProjectProperty.parcel_number,
        ProjectProperty.rental_registration_number,
        ProjectProperty.created_at,
        ProjectProperty.updated_at,
    ]
    column_searchable_list: ClassVar = [
        ProjectProperty.address,
        ProjectProperty.owner_lcc_name,
        ProjectProperty.parcel_number,
        ProjectProperty.rental_registration_number,
    ]
    column_sortable_list: ClassVar = [
        ProjectProperty.id,
        ProjectProperty.project_id,
        ProjectProperty.address,
        ProjectProperty.type,
        ProjectProperty.year_of_construction,
        ProjectProperty.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(ProjectProperty.type, title='Building Type'),
    ]
    form_excluded_columns: ClassVar = [
        ProjectProperty.created_at,
        ProjectProperty.updated_at,
        ProjectProperty.deleted_at,
        ProjectProperty.project,
        ProjectProperty.structures,
        ProjectProperty.jobs,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }


class PropertyStructureAdmin(TimestampAdminMixin, ModelView, model=PropertyStructure):
    name = 'Property Structure'
    name_plural = 'Property Structures'
    icon = 'fa-solid fa-building-columns'

    column_list: ClassVar = [
        PropertyStructure.id,
        PropertyStructure.property_id,
        PropertyStructure.address,
        PropertyStructure.type,
        PropertyStructure.number_of_units,
        PropertyStructure.created_at,
        PropertyStructure.updated_at,
    ]
    column_searchable_list: ClassVar = [
        PropertyStructure.address,
    ]
    column_sortable_list: ClassVar = [
        PropertyStructure.id,
        PropertyStructure.property_id,
        PropertyStructure.address,
        PropertyStructure.type,
        PropertyStructure.created_at,
    ]
    column_filters: ClassVar = [
        AllUniqueStringValuesFilter(PropertyStructure.type, title='Building Type'),
    ]
    form_excluded_columns: ClassVar = [
        PropertyStructure.created_at,
        PropertyStructure.updated_at,
        PropertyStructure.deleted_at,
        PropertyStructure.property,
    ]

    form_args: ClassVar = {
        **TimestampAdminMixin.form_args,
    }

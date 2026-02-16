from typing import Annotated, Self

from pydantic import Field, model_validator

from core import BaseModelSchema
from models.projects import BuildingTypeEnum


class CreateStructureRequestSchema(BaseModelSchema):
    """Schema for creating a structure under a MULTI_STRUCTURE property."""

    structure_address: Annotated[
        str,
        Field(
            description='Address of the structure',
            min_length=1,
            max_length=255,
        ),
    ]
    structure_type: Annotated[
        BuildingTypeEnum,
        Field(
            description='Type of the structure (cannot be MULTI_STRUCTURE)',
        ),
    ]
    number_of_units: Annotated[
        int,
        Field(description='Number of units', ge=0),
    ]

    @model_validator(mode='after')
    def validate_structure_type(self) -> Self:
        if self.structure_type == BuildingTypeEnum.MULTI_STRUCTURE:
            raise ValueError('Structure type cannot be MULTI_STRUCTURE')
        return self


class CreatePropertyRequestSchema(BaseModelSchema):
    """Schema for creating a property within a project."""

    address: Annotated[
        str,
        Field(
            description='Property address',
            examples=['123 Main Street'],
            min_length=1,
            max_length=255,
        ),
    ]
    type: Annotated[
        BuildingTypeEnum,
        Field(
            description='Type of the property',
            examples=[BuildingTypeEnum.SINGLE_FAMILY],
        ),
    ]
    number_of_units: Annotated[
        int,
        Field(description='Number of units', examples=[1], ge=0),
    ]
    owner_lcc_name: Annotated[
        str | None,
        Field(
            default=None,
            description='Owner LCC name',
            examples=['John Doe'],
            max_length=255,
        ),
    ]
    year_of_construction: Annotated[
        int | None,
        Field(
            default=None,
            description='Year of construction',
            examples=[2020],
        ),
    ]
    parcel_number: Annotated[
        str | None,
        Field(
            default=None,
            description='Parcel number',
            examples=['12345678'],
            max_length=255,
        ),
    ]
    registration_number: Annotated[
        str | None,
        Field(
            default=None,
            description='Rental registration number',
            examples=['12345678'],
            max_length=255,
        ),
    ]
    structures: Annotated[
        list[CreateStructureRequestSchema],
        Field(
            default_factory=list,
            description='Structures (only when type is MULTI_STRUCTURE)',
        ),
    ]

    @model_validator(mode='after')
    def validate_structures_only_for_multi(self) -> Self:
        if self.type != BuildingTypeEnum.MULTI_STRUCTURE and self.structures:
            raise ValueError(
                'Structures can only be provided when property type is MULTI_STRUCTURE'
            )
        return self


class CreateProjectRequestSchema(BaseModelSchema):
    """Schema for creating a project with properties."""

    client_id: Annotated[
        int,
        Field(
            description='Client id',
            gt=0,
            examples=[1],
        ),
    ]
    project_name: Annotated[
        str,
        Field(
            description='Project name',
            examples=['Project for renovate'],
            min_length=1,
            max_length=255,
        ),
    ]
    property_manager: Annotated[
        str | None,
        Field(
            default=None,
            description='Property manager name',
            examples=['John Doe'],
            max_length=255,
        ),
    ]
    properties: Annotated[
        list[CreatePropertyRequestSchema],
        Field(description='List of properties', min_length=1),
    ]


class PropertyStructureResponseSchema(BaseModelSchema):
    """Schema for a property structure in response."""

    id: int
    address: str
    type: BuildingTypeEnum
    number_of_units: int


class ProjectPropertyResponseSchema(BaseModelSchema):
    """Schema for a project property in response."""

    id: int
    address: str
    type: BuildingTypeEnum
    number_of_units: int
    owner_lcc_name: str | None
    year_of_construction: int | None
    parcel_number: str | None
    rental_registration_number: str | None
    structures: list[PropertyStructureResponseSchema] = []


class ProjectResponseSchema(BaseModelSchema):
    """Schema for project in response."""

    id: int
    client_id: int
    project_name: str
    property_manager_name: str | None
    properties: list[ProjectPropertyResponseSchema] = []


class _OngoingProjectResponseSchema(BaseModelSchema):
    amount: int
    scheduled: int
    need_scheduled: int
    completed_this_week: int

class _NeedSchedulingResponseSchema(BaseModelSchema):
    amount: int
    project_names: list[str]

class _UnassignedProjectResponseSchema(BaseModelSchema):
    amount: int
    project_names: list[str]

class _RentalProjectResponseSchema(BaseModelSchema):
    amount: int
    project_names: list[str]

class ProjectDashboardResponseSchema(BaseModelSchema):
    ongoing_project: _OngoingProjectResponseSchema
    need_scheduling: _NeedSchedulingResponseSchema
    unassigned_jobs: _UnassignedProjectResponseSchema
    ready_for_finalize: _RentalProjectResponseSchema
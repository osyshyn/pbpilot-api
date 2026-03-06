from datetime import date, datetime
from typing import Annotated, Self

from fastapi import Query
from pydantic import EmailStr, Field, model_validator

from core import BaseModelSchema, BaseUpdateSchema
from models.projects import BuildingTypeEnum, ProjectStatusEnum


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


class UpdateProjectRequestSchema(BaseUpdateSchema):
    """Schema for updating project and its contact information."""

    project_name: Annotated[
        str | None,
        Field(
            default=None,
            description='Project name',
            examples=['Updated project name'],
            min_length=1,
            max_length=255,
        ),
    ]
    email: Annotated[
        EmailStr | None,
        Field(
            default=None,
            description='Contact email for the project',
            examples=['project_contact@example.com'],
        ),
    ]
    phone_number: Annotated[
        str | None,
        Field(
            default=None,
            description='Contact phone number for the project',
            examples=['+12345678901'],
            min_length=3,
            max_length=128,
        ),
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
    status: ProjectStatusEnum
    property_manager_name: str | None
    properties: list[ProjectPropertyResponseSchema] = []
    created_at: datetime


class ProjectInformationResponseSchema(BaseModelSchema):
    """Aggregated information about the project."""

    project_name: str
    total_properties: int
    total_units: int
    created_date: datetime
    last_updated: datetime


class ProjectContactDetailsResponseSchema(BaseModelSchema):
    """Contact information for the project client."""

    client_fullname: str
    client_phone: str | None
    client_email: str


class ProjectLabResultResponseSchema(BaseModelSchema):
    """Laboratory result information for the project."""

    laboratory_name: str
    match_status: str
    status: str


class ProjectReportResponseSchema(BaseModelSchema):
    """Report information for the project."""

    report_name: str
    creation_date: datetime


class ProjectDetailsResponseSchema(BaseModelSchema):
    """Full project details grouped into sections."""

    project_information: ProjectInformationResponseSchema
    contact_details: ProjectContactDetailsResponseSchema
    lab_results: list[ProjectLabResultResponseSchema] = []
    reports: list[ProjectReportResponseSchema] = []


class _OngoingProjectResponseSchema(BaseModelSchema):
    amount: Annotated[
        int,
        Field(description='Amount', examples=[21]),
    ]
    scheduled: Annotated[
        int,
        Field(description='Scheduled', examples=[12]),
    ]
    need_scheduled: Annotated[
        int,
        Field(description='Need scheduled', examples=[5]),
    ]
    completed_this_week: Annotated[
        int,
        Field(description='Completed this week', examples=[7]),
    ]


class _NeedSchedulingResponseSchema(BaseModelSchema):
    amount: Annotated[
        int,
        Field(description='Amount', examples=[6]),
    ]
    project_names: Annotated[
        list[str],
        Field(
            description='Project names',
            examples=[
                'Westbrook Family Housing',
                '8123 Canton Ridge',
                'Maple Street Duplex',
            ],
        ),
    ]


class _UnassignedProjectResponseSchema(BaseModelSchema):
    amount: Annotated[
        int,
        Field(description='Amount', examples=[3]),
    ]

    project_names: Annotated[
        list[str],
        Field(
            description='Project names',
            examples=['8123 Canton Ridge', 'Lincoln bridge'],
        ),
    ]


class _RentalProjectResponseSchema(BaseModelSchema):
    amount: Annotated[
        int,
        Field(description='Amount', examples=[3]),
    ]

    project_names: Annotated[
        list[str],
        Field(
            description='Project names',
            examples=['9632 Canton Ridge', 'Oakridge Townhomes'],
        ),
    ]


class ProjectDashboardResponseSchema(BaseModelSchema):
    ongoing_project: _OngoingProjectResponseSchema
    need_scheduling: _NeedSchedulingResponseSchema
    unassigned_jobs: _UnassignedProjectResponseSchema
    ready_for_finalize: _RentalProjectResponseSchema


class ProjectFiltersSchema:
    """Dependency class for filtering projects list."""

    def __init__(
        self,
        status: ProjectStatusEnum | None = Query(
            default=None,
            description='Filter by project status',
        ),
        client_id: int | None = Query(
            default=None,
            description='Filter by client id',
            gt=0,
        ),
        inspector_id: int | None = Query(
            default=None,
            description='Filter by inspector id (projects that have at least one job assigned to this inspector)',
            gt=0,
        ),
        date: date | None = Query(
            default=None,
            description='Filter by creation date (YYYY-MM-DD)',
        ),
    ) -> None:
        self.status = status
        self.client_id = client_id
        self.inspector_id = inspector_id
        self.date = date


class ProjectFileSchema(BaseModelSchema):
    """Schema for a single project file (S3 object)."""

    key: Annotated[
        str,
        Field(description='S3 object key'),
    ]
    url: Annotated[
        str,
        Field(description='Pre-signed S3 URL for downloading the file'),
    ]
    file_type: Annotated[
        str,
        Field(
            description='Category of the file, e.g. report, lab_result, license_image',
            examples=['report', 'lab_result', 'license_image'],
        ),
    ]
    filename: Annotated[
        str,
        Field(
            description='Human-friendly file name',
            examples=['Initial Report.pdf'],
        ),
    ]


class ProjectFilesResponseSchema(BaseModelSchema):
    """Response schema for project files download list."""

    files: Annotated[
        list[ProjectFileSchema],
        Field(
            description='List of files associated with the project (S3 pre-signed URLs)',
            default_factory=list,
        ),
    ]
    total: Annotated[
        int,
        Field(description='Total number of files', examples=[3]),
    ]

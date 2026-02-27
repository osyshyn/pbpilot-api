from datetime import date as DateType
from datetime import datetime
from typing import Annotated

from pydantic import Field

from core import BaseModelSchema
from models.jobs import InspectionTypeEnum, JobStatusEnum
from models.projects import BuildingTypeEnum, ProjectStatusEnum


class JobListFiltersSchema(BaseModelSchema):
    """Optional filters for listing jobs by project."""

    status: JobStatusEnum | None = Field(
        default=None,
        description='Filter by job status',
    )
    inspector_id: int | None = Field(
        default=None,
        description='Filter by inspector id',
        gt=0,
    )
    date: DateType | None = Field(
        default=None,
        description='Filter by job creation date',
    )


class CreateJobRequestSchema(BaseModelSchema):
    property_id: Annotated[
        int,
        Field(
            description='ID of the project property',
            gt=0,
            examples=[1],
        ),
    ]
    inspector_id: Annotated[
        int | None,
        Field(
            default=None,
            description='ID of assigned inspector (optional)',
            gt=0,
            examples=[1],
        ),
    ]
    inspection_type: Annotated[
        InspectionTypeEnum,
        Field(
            description='Type of inspection',
            examples=[InspectionTypeEnum.CLEARANCE],
        ),
    ]
    notes: Annotated[
        str | None,
        Field(
            default=None,
            description='Additional notes for the job',
            max_length=2048,
        ),
    ]


class AssignInspectorRequestSchema(BaseModelSchema):
    """Schema for assigning or unassigning inspector to a job."""

    inspector_id: Annotated[
        int | None,
        Field(
            default=None,
            description='ID of assigned inspector (nullable to unassign)',
            gt=0,
            examples=[1],
        ),
    ]


class JobResponseSchema(BaseModelSchema):
    id: int
    property_id: int
    inspector_id: int | None
    inspection_type: InspectionTypeEnum
    notes: str | None


class JobInfoResponseSchema(BaseModelSchema):
    job_type: InspectionTypeEnum
    owner_name: str
    property_manager: str | None
    owner_business_address: str
    owner_email: str
    owner_phone_number: str | None
    status: ProjectStatusEnum
    inspector: str | None
    created_at: datetime
    scheduled_time: datetime | None
    progress_percent: int


class JobPropertyDetailsResponseSchema(BaseModelSchema):
    property_address: str
    structure_type: BuildingTypeEnum
    number_of_units: int
    inspection_date: datetime | None
    owner_lcc_name: str | None
    year_of_construction: int | None
    parcel_number: str | None
    rental_registration_number: str | None


class JobInspectionProgressResponseSchema(BaseModelSchema):
    job_created: bool
    inspection_scheduled: bool
    inspection_completed: bool
    lab_results_received: bool
    invoice_sent_to_client: bool
    report_generated: bool
    report_sent_to_client: bool


class JobDetailsResponseSchema(BaseModelSchema):
    job: JobInfoResponseSchema
    property: JobPropertyDetailsResponseSchema
    progress: JobInspectionProgressResponseSchema
    notes: str | None


class JobListItemResponseSchema(BaseModelSchema):
    property_address: str
    status: ProjectStatusEnum
    job_type: InspectionTypeEnum
    inspector: str | None
    units: int
    progress: int
    date_created: datetime

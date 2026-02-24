from typing import Annotated

from pydantic import Field

from core import BaseModelSchema
from models.jobs import InspectionTypeEnum


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


class JobResponseSchema(BaseModelSchema):
    id: int
    property_id: int
    inspector_id: int | None
    inspection_type: InspectionTypeEnum
    notes: str | None


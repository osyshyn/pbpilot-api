from __future__ import annotations

from typing import List
from uuid import UUID

from pydantic import Field, model_validator

from core import BaseModelSchema
from models.jobs import InspectionTypeEnum, SampleTypeEnum
from models.observation import ObservationCategoryEnum


class PhotoSyncSchema(BaseModelSchema):
    id: UUID = Field(description='Client-generated UUID for the photo')
    s3_key: str = Field(
        max_length=512,
        description='S3 key of the photo object',
    )
    descriptions: str | None = Field(
        default=None,
        max_length=1024,
        description='Optional descriptions/caption for the photo',
    )


class ObservationSyncSchema(BaseModelSchema):
    id: UUID = Field(description='Client-generated UUID for the observation')
    category: ObservationCategoryEnum = Field(
        description=(
            'Observation category: HAZARD, FUTURE_RISK, EXCLUSION, or INFO '
            '(e.g. for title-page / general photos in PDF reports).'
        ),
    )
    component: str = Field(
        max_length=255,
        description='Inspected component (e.g. window sill, door frame)',
    )
    side: str | None = Field(
        default=None,
        max_length=50,
        description='Side label (A, B, C, D, All) if applicable',
    )
    condition: str | None = Field(
        default=None,
        max_length=255,
        description='Condition description (peeling, intact, etc.)',
    )
    identifiers: str | None = Field(
        default=None,
        max_length=255,
        description='Identifiers or numeric ranges from the report',
    )
    raw_text: str | None = Field(
        default=None,
        max_length=1024,
        description='Original text fragment from the report',
    )
    photos: List[PhotoSyncSchema] = Field(
        default_factory=list,
        description='Photos linked to this observation',
    )


class RoomSyncSchema(BaseModelSchema):
    id: UUID = Field(description='Client-generated UUID for the room')
    name: str = Field(
        max_length=255,
        description='Room or section name',
    )
    observations: List[ObservationSyncSchema] = Field(
        default_factory=list,
        description='Interior observations within this room',
    )


class SampleSyncSchema(BaseModelSchema):
    id: UUID = Field(description='Client-generated UUID for the sample')
    sample_type: SampleTypeEnum = Field(
        description='Type of environmental sample',
    )
    barcode_id: str = Field(
        max_length=100,
        description='Short barcode / identifier for the sample',
    )
    location_description: str | None = Field(
        default=None,
        max_length=512,
        description='Human-readable location description',
    )
    side: str | None = Field(
        default=None,
        max_length=50,
        description='Side label for paint chips or similar samples',
    )
    component: str | None = Field(
        default=None,
        max_length=255,
        description='Component for which the sample was taken',
    )
    soil_area: str | None = Field(
        default=None,
        max_length=100,
        description='Soil area type (e.g. Dripline, Play Area)',
    )
    photo_s3_key: str | None = Field(
        default=None,
        max_length=512,
        description='Deprecated: use photos[].s3_key. Single photo S3 key for backward compatibility.',
    )
    photos: List[PhotoSyncSchema] = Field(
        default_factory=list,
        description='Photos of the sampling location (multiple allowed)',
    )


class COCFormSyncSchema(BaseModelSchema):
    id: UUID = Field(description='Client-generated UUID for the COC form')
    is_active: bool = Field(
        default=True,
        description='Whether this COC form is active',
    )
    samples: List[SampleSyncSchema] = Field(
        default_factory=list,
        description='Samples attached to this COC form',
    )


class UnitSyncSchema(BaseModelSchema):
    id: UUID = Field(description='Client-generated UUID for the unit')
    name: str = Field(
        max_length=255,
        description='Unit name or identifier (e.g. Unit 2A)',
    )
    is_common_area: bool = Field(
        description='Whether this unit represents a common area',
    )
    floor_plan_s3_key: str | None = Field(
        default=None,
        max_length=512,
        description='S3 key of the unit floor plan',
    )
    floor_plan_data: dict | None = Field(
        default=None,
        description='Arbitrary JSON data for floor plan geometry',
    )
    rooms: List[RoomSyncSchema] = Field(
        default_factory=list,
        description='Rooms within this unit',
    )
    coc_forms: List[COCFormSyncSchema] = Field(
        default_factory=list,
        description='Unit-scoped COC forms for interior samples',
    )


class JobSyncRequestSchema(BaseModelSchema):
    inspection_type: InspectionTypeEnum = Field(
        description='Inspection type for the job',
    )
    notes: str | None = Field(
        default=None,
        max_length=2048,
        description='General property condition / inspection notes (e.g. from Property Condition step)',
    )
    units: List[UnitSyncSchema] = Field(
        default_factory=list,
        description='Interior units with rooms, observations and COC forms',
    )
    exterior_observations: List[ObservationSyncSchema] = Field(
        default_factory=list,
        description='Exterior observations (no room binding)',
    )
    exterior_coc_forms: List[COCFormSyncSchema] = Field(
        default_factory=list,
        description='COC forms not bound to a specific unit (exterior)',
    )

    @model_validator(mode='after')
    def validate_inspection_business_rules(
        self,
    ) -> JobSyncRequestSchema:
        """Validate high-level business rules per inspection type."""
        all_coc_forms = list(self.exterior_coc_forms)
        for unit in self.units:
            all_coc_forms.extend(unit.coc_forms)

        dust_wipes_count = sum(
            1
            for form in all_coc_forms
            for sample in form.samples
            if sample.sample_type is SampleTypeEnum.DUST_WIPE
        )

        if self.inspection_type is InspectionTypeEnum.RISK_ASSESSMENT:
            if dust_wipes_count != 11:
                msg = (
                    'Risk Assessment requires exactly 11 Dust Wipe samples, '
                    f'got {dust_wipes_count}.'
                )
                raise ValueError(msg)
        elif self.inspection_type is InspectionTypeEnum.CLEARANCE:
            if dust_wipes_count != 13:
                msg = (
                    'Clearance requires exactly 13 Dust Wipe samples, '
                    f'got {dust_wipes_count}.'
                )
                raise ValueError(msg)
        elif self.inspection_type is InspectionTypeEnum.PRE_INSPECTION:
            if all_coc_forms or dust_wipes_count > 0:
                msg = (
                    'Pre-Inspection cannot have COC forms or '
                    'environmental samples.'
                )
                raise ValueError(msg)
        elif self.inspection_type is InspectionTypeEnum.RETEST:
            # RETEST: no fixed dust-wipe count; depends on how many areas were repaired.
            # Validator allows any number of samples (including 0).
            pass
        return self


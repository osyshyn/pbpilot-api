"""Schemas for Lead-Based Paint parsing API."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ObservationCategoryEnum(StrEnum):
    """Enumeration of observation categories."""

    HAZARD = 'HAZARD'
    FUTURE_RISK = 'FUTURE_RISK'
    EXCLUSION = 'EXCLUSION'


class ParseTextRequestSchema(BaseModel):
    """Request schema for parsing lead paint inspection text."""

    text: str = Field(
        ...,
        min_length=1,
        description='Raw text from inspection report',
        examples=[
            'Side A\n\nWood siding, all sides, evidence of peeling/chipping'
        ],
    )
    unit_name: str | None = Field(
        default=None,
        description='Optional unit name when text describes a single unit (e.g. "Unit 2A"). '
        'If provided, all observations will have their unit set to this value. '
        'Leave null for common areas (e.g. stairwell, hallway).',
    )


class ObservationResponseSchema(BaseModel):
    """Response schema for a single observation."""

    category: ObservationCategoryEnum
    is_exterior: bool
    unit: str | None = None
    room: str | None = None
    component: str
    side: str | None = None
    condition: str | None = None
    identifiers: str | None = None
    raw_text: str = Field(
        description=(
            "The exact original line or bullet point from the input text that was "
            "used to generate this observation."
        ),
    )


class UnitHazardsSchema(BaseModel):
    """Per-unit structure: hazards keyed by room name."""

    hazards: dict[str, list[ObservationResponseSchema]] = Field(
        default_factory=dict,
        description='Room name -> list of observations',
    )


class HazardsGroupedSchema(BaseModel):
    """Hazards (or future_risk) grouped by unit and by room.

    - by_unit: unit id -> { "hazards": { room name -> list of observations } }.
    - by_room: room/section name -> list of observations (when unit is null).
    """

    by_unit: dict[str, UnitHazardsSchema] = Field(
        default_factory=dict,
        description='Unit id -> { hazards: { room name -> observations } }',
    )
    by_room: dict[str, list[ObservationResponseSchema]] = Field(
        default_factory=dict,
        description='Room/section name -> observations (when no unit)',
    )


class ParseTextResponseSchema(BaseModel):
    """Response schema for parsing endpoints.

    hazards and future_risk are grouped by unit and room.
    excluded_components is a flat list.
    """

    hazards: HazardsGroupedSchema = Field(
        default_factory=HazardsGroupedSchema,
        description='Hazard observations grouped by unit and room',
    )
    future_risk: HazardsGroupedSchema = Field(
        default_factory=HazardsGroupedSchema,
        description='Future risk observations grouped by unit and room',
    )
    excluded_components: list[ObservationResponseSchema] = Field(
        default_factory=list,
        description='Excluded components (category=EXCLUSION)',
    )

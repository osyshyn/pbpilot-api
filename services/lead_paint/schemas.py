"""Pydantic schemas for Lead-Based Paint parsing.

Used as structured output for LLM extraction.
"""

import re

from pydantic import BaseModel, Field, field_validator

_JSON_ARTIFACT_RE = re.compile(r'[,\s]*[{\[].*$')


def _strip_json_artifacts(s: str | None) -> str | None:
    if s is None:
        return None
    cleaned = _JSON_ARTIFACT_RE.sub('', s).strip()
    return cleaned if cleaned else None


def _null_if_empty(s: str | None) -> str | None:
    """Treat empty string or literal 'null' as None."""
    if s is None:
        return None
    s = s.strip()
    if not s or s.lower() == 'null':
        return None
    return s


class ObservationSchema(BaseModel):
    """Single observation (hazard, future risk, or exclusion)."""

    category: str = Field(
        description="Must be 'HAZARD', 'FUTURE_RISK', or 'EXCLUSION'"
    )
    is_exterior: bool = Field(description='True if exterior, False if interior')
    unit: str | None = Field(
        default=None,
        description="Unit name, e.g., 'Unit Down', 'Unit 1'. Null if exterior.",
    )
    room: str | None = Field(
        default=None,
        description="Room name, e.g., 'Living Room', 'Kitchen'. Null if exterior.",
    )
    component: str = Field(
        description="The item inspected, e.g., 'Window Sill', 'Door Frame'"
    )
    side: str | None = Field(
        default=None,
        description="Side of building/room: 'A', 'B', 'C', 'D', or 'All'",
    )
    condition: str | None = Field(
        default=None,
        description="Condition, e.g., 'painted', 'enclosed', 'new', 'unpainted'",
    )
    identifiers: str | None = Field(
        default=None,
        description="Any numbers or IDs, e.g., '1-2', '1-5'. Leave null if none.",
    )
    raw_text: str = Field(
        description=(
            'The exact original line or bullet point from the input text that was '
            'used to generate this observation.'
        ),
    )

    @field_validator('condition', 'unit', 'room', 'side', 'identifiers')
    @classmethod
    def strip_json_artifacts_optional(cls, v: str | None) -> str | None:
        v = _strip_json_artifacts(v)
        return _null_if_empty(v)

    @field_validator('component')
    @classmethod
    def strip_json_artifacts_component(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            return v or ''
        cleaned = _JSON_ARTIFACT_RE.sub('', v).strip()
        return cleaned if cleaned else v

    @field_validator('side')
    @classmethod
    def normalize_side(cls, v: str | None) -> str | None:
        if v is None or not v:
            return None
        v = v.strip()
        if v.lower() == 'all':
            return 'All'
        if v.upper() in ('A', 'B', 'C', 'D'):
            return v.upper()
        if (
            v in ('1', '2', '3', 'two', '1-2', '1-3')
            or v.replace('-', '').isdigit()
        ):
            return None
        return v

    @field_validator('raw_text')
    @classmethod
    def normalize_raw_text(cls, v: str | None) -> str:
        """Normalize raw_text: trim and strip bullet characters like '●', '-', '*', '•'."""
        if v is None:
            return ''
        v = v.strip()
        while v and v[0] in {'●', '-', '*', '•'}:
            v = v[1:].lstrip()
        cleaned = _strip_json_artifacts(v)
        return cleaned if cleaned is not None else v


class SectionExtractionSchema(BaseModel):
    """Wrapper for list of observations returned by parser."""

    observations: list[ObservationSchema]

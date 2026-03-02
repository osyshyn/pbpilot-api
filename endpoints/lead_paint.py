"""Endpoints for Lead-Based Paint inspection parsing."""

import logging

from fastapi import APIRouter, HTTPException, status
from langchain_core.exceptions import LangChainException

from schemas import (
    HazardsGroupedSchema,
    ObservationResponseSchema,
    ParseTextRequestSchema,
    ParseTextResponseSchema,
    UnitHazardsSchema,
)
from services.lead_paint import LeadPaintService
from services.lead_paint.grouping import (
    group_by_unit_and_room,
    group_observations_by_category,
)
from services.lead_paint.schemas import ObservationSchema

logger = logging.getLogger(__name__)

lead_paint_router = APIRouter()

_lead_paint_service = LeadPaintService()


def _obs_to_response(obs: ObservationSchema) -> ObservationResponseSchema:
    return ObservationResponseSchema(**obs.model_dump())


def _build_grouped_schema(
    observations: list[ObservationSchema],
    use_side_as_room: bool = False,
) -> HazardsGroupedSchema:
    """Build HazardsGroupedSchema from flat list (by unit and by room)."""
    by_unit_raw, by_room_raw = group_by_unit_and_room(
        observations, use_side_as_room=use_side_as_room
    )
    by_unit: dict[str, UnitHazardsSchema] = {}
    for unit_id, rooms in by_unit_raw.items():
        room_to_list = {
            room: [_obs_to_response(o) for o in obs_list]
            for room, obs_list in rooms.items()
        }
        by_unit[unit_id] = UnitHazardsSchema(hazards=room_to_list)
    by_room = {
        room: [_obs_to_response(o) for o in obs_list]
        for room, obs_list in by_room_raw.items()
    }
    return HazardsGroupedSchema(by_unit=by_unit, by_room=by_room)


def _build_categorized_response(
    observations: list[ObservationSchema],
    *,
    use_side_as_room: bool = False,
) -> ParseTextResponseSchema:
    """Split into hazards / future_risk / excluded; group hazards and future_risk by unit/room."""
    hazards_list, future_risk_list, excluded_list = group_observations_by_category(
        observations
    )
    return ParseTextResponseSchema(
        hazards=_build_grouped_schema(hazards_list, use_side_as_room=use_side_as_room),
        future_risk=_build_grouped_schema(
            future_risk_list, use_side_as_room=use_side_as_room
        ),
        excluded_components=[_obs_to_response(o) for o in excluded_list],
    )


@lead_paint_router.post(
    path='/parse-exterior',
    summary='Parse exterior observations (hazards and exclusions)',
    response_model=ParseTextResponseSchema,
)
async def parse_exterior(
    request: ParseTextRequestSchema,
) -> ParseTextResponseSchema:
    """Parse exterior text containing hazards and/or exclusions.

    Extracts observations from exterior inspection text (Side A/B/C/D).
    LLM determines category (HAZARD or EXCLUSION) from context (headers).
    All observations will have is_exterior=True, unit=null, room=null.
    Grouped by Side (Side A, Side B, etc.) in by_room.

    Args:
        request: Request with raw inspection text (may include Excluded components).

    Returns:
        ParseTextResponseSchema with hazards and excluded_components.

    Raises:
        400: If text is empty.
        500: If OpenAI API fails.

    """
    try:
        observations = await _lead_paint_service.parse_exterior_async(request.text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except LangChainException as e:
        logger.exception('OpenAI API error')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to parse text using OpenAI API',
        ) from e

    return _build_categorized_response(observations, use_side_as_room=True)


@lead_paint_router.post(
    path='/parse-interior',
    summary='Parse interior observations (hazards and exclusions)',
    response_model=ParseTextResponseSchema,
)
async def parse_interior(
    request: ParseTextRequestSchema,
) -> ParseTextResponseSchema:
    """Parse interior text containing hazards and/or exclusions.

    The mobile app sends text for a SINGLE unit or common area per request.
    If request.unit_name is provided, all observations are assigned that unit;
    otherwise unit stays null (common areas).

    Extracts observations from interior inspection text (Room -> Component).
    LLM determines category (HAZARD or EXCLUSION) from context (headers).
    Handles complex exclusions like "Excluded components: living room, kitchen, vinyl floors"
    by creating separate observations for each room with the component.
    Hazards (and future_risk) are grouped by unit and room.

    Args:
        request: Request with raw inspection text and optional unit_name.

    Returns:
        ParseTextResponseSchema with hazards/future_risk grouped by unit and room,
        and excluded_components as flat list.

    Raises:
        400: If text is empty.
        500: If OpenAI API fails.

    """
    unit_name: str | None = None
    if request.unit_name is not None:
        stripped = request.unit_name.strip()
        if stripped:
            unit_name = stripped

    try:
        observations = await _lead_paint_service.parse_interior_async(
            request.text,
            unit_name=unit_name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except LangChainException as e:
        logger.exception('OpenAI API error')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to parse text using OpenAI API',
        ) from e

    return _build_categorized_response(observations, use_side_as_room=False)

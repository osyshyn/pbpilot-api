"""Lead-Based Paint parsers for exterior and interior sections."""

from typing import cast

from langchain_core.prompts import ChatPromptTemplate

from services.lead_paint.llm import get_async_structured_llm, get_structured_llm
from services.lead_paint.schemas import (
    ObservationSchema,
    SectionExtractionSchema,
)

_EXTERIOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            """You are an expert data extraction bot for Lead-Based Paint Inspections.
Your task is to extract observations from the EXTERIOR of a building.

CRITICAL RULES:
1. Track the 'Side' (A, B, C, D). If elements are listed under "Side A", their side is "A".
2. Each bullet point (●) or line represents a separate component.
3. Track the CATEGORY from context:
   - If items are under a header like "Exterior lead hazards" or no exclusion/future risk header, set category to 'HAZARD'.
   - If items are under a header like "Future risks", "Potential hazards", or "Future risk", set category to 'FUTURE_RISK'.
   - If items are under a header like "Excluded components", set category to 'EXCLUSION'.
4. is_exterior MUST be True. Unit and Room MUST be null for all exterior items.
5. Extract component: the main item (e.g., Wood siding, Front entry door, Foundation, Rear porch decking).
6. ALWAYS extract condition when the text implies one:
   - Condition at the END: "Foundation painted" → component="Foundation", condition="painted". "Rear porch, decking, handrail, steps" has no condition → condition=null.
   - Condition at the START: "Painted window blinds, second floor" → component="window blinds", condition="painted", identifiers="second floor" if applicable.
   - Common condition values: painted, unpainted, enclosed, new, chipping, peeling, intact to paint. If the line only lists component names with no condition word, leave condition null.
7. Extract identifiers (e.g., "second floor", "1-6", "1-9 SB") when present.
8. side MUST be only one of: A, B, C, D, or All. If no side is stated, leave side null.
9. For each observation, copy the EXACT original line or bullet point from the input text into the `raw_text` field. Do not summarize or rephrase it; only trim leading bullet characters and surrounding whitespace.
10. If a single input line or bullet results in multiple observations, use that same original line as `raw_text` for ALL of those observations.

OUTPUT FORMAT: Put only plain text in every field. Never include JSON syntax inside field values.""",
        ),
        ('user', 'Text:\n\n{text}'),
    ]
)

_INTERIOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            """You are an expert data extraction bot for Lead-Based Paint Inspections.
Your task is to parse INTERIOR hazards and exclusions into observations.

CRITICAL RULES:
1. The text describes the interior of a SINGLE unit or a common area. You DO NOT need to extract the unit name. Focus only on the rooms and components.
2. Track the CURRENT ROOM (e.g., 'Living room', 'Kitchen'). If there is no specific room mentioned at the top, use the section name as the room.
3. Each bullet point (●) or line represents a separate component.
4. Track the CATEGORY from context:
   - Default category is 'HAZARD'.
   - If you see a header like "Future risks", "Potential hazards", or "Future risk", change category to 'FUTURE_RISK'.
   - If you see "Excluded components", change category to 'EXCLUSION'.
5. COMPLEX EXCLUSIONS RULE: If you see a comma-separated list of rooms followed by a component (e.g., "Excluded components: living room, bedroom, kitchen, vinyl floors"), you MUST create a separate observation for EACH room. The `component` field MUST be the actual item (e.g., "vinyl floors"), NEVER the words "Excluded components". Example output: Room: "living room", Component: "vinyl floors". Room: "bedroom", Component: "vinyl floors".
6. Extract side (A, B, C, D, All) if mentioned.
7. is_exterior MUST be False.
8. For each observation, copy the EXACT original line or bullet point from the input text into the `raw_text` field. Do not summarize or rephrase it; only trim leading bullet characters and surrounding whitespace.

Extract component and condition from each line. Put only plain text in every field. Never include JSON syntax inside field values. For missing values, use null.""",
        ),
        ('user', 'Text:\n\n{text}'),
    ]
)


def parse_exterior_text(text: str) -> list[ObservationSchema]:
    """Parse exterior lead hazards text into observations (sync).

    Args:
        text: Raw text containing exterior hazards (with Side A/B/C/D headers).

    Returns:
        List of ObservationSchema objects with is_exterior=True.

    """
    if not text.strip():
        return []

    result = cast(
        SectionExtractionSchema,
        (_EXTERIOR_PROMPT | get_structured_llm()).invoke({'text': text}),
    )
    return result.observations


async def parse_exterior_text_async(text: str) -> list[ObservationSchema]:
    """Parse exterior lead hazards text into observations (async).

    Args:
        text: Raw text containing exterior hazards (with Side A/B/C/D headers).

    Returns:
        List of ObservationSchema objects with is_exterior=True.

    """
    if not text.strip():
        return []

    result = cast(
        SectionExtractionSchema,
        await (_EXTERIOR_PROMPT | get_async_structured_llm()).ainvoke(
            {'text': text}
        ),
    )
    return result.observations


def parse_interior_text(text: str) -> list[ObservationSchema]:
    """Parse interior lead hazards text into observations (sync).

    Args:
        text: Raw text containing interior hazards (single unit or common area).

    Returns:
        List of ObservationSchema objects with is_exterior=False.

    """
    if not text.strip():
        return []

    result = cast(
        SectionExtractionSchema,
        (_INTERIOR_PROMPT | get_structured_llm()).invoke({'text': text}),
    )
    return result.observations


async def parse_interior_text_async(text: str) -> list[ObservationSchema]:
    """Parse interior lead hazards text into observations (async).

    Args:
        text: Raw text containing interior hazards (single unit or common area).

    Returns:
        List of ObservationSchema objects with is_exterior=False.

    """
    if not text.strip():
        return []

    result = cast(
        SectionExtractionSchema,
        await (_INTERIOR_PROMPT | get_async_structured_llm()).ainvoke(
            {'text': text}
        ),
    )
    return result.observations

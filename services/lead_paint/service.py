"""Lead-Based Paint parsing service."""

import logging

from langchain_core.exceptions import LangChainException

from services.lead_paint.parsers import (
    parse_exterior_text,
    parse_exterior_text_async,
    parse_interior_text,
    parse_interior_text_async,
)
from services.lead_paint.schemas import ObservationSchema

logger = logging.getLogger(__name__)


class LeadPaintService:
    """Service for parsing Lead-Based Paint inspection text."""

    def parse_exterior(self, text: str) -> list[ObservationSchema]:
        """Parse exterior hazards text (sync).

        Args:
            text: Raw text containing exterior hazards.

        Returns:
            List of ObservationSchema objects.

        Raises:
            ValueError: If text is empty.
            LangChainException: If OpenAI API fails.

        """
        if not text.strip():
            raise ValueError('Exterior text cannot be empty')

        try:
            observations = parse_exterior_text(text)
            logger.info(f'Parsed {len(observations)} exterior observations')
            return observations
        except LangChainException:
            logger.exception('OpenAI API error during exterior parsing')
            raise

    async def parse_exterior_async(self, text: str) -> list[ObservationSchema]:
        """Parse exterior hazards text (async).

        Args:
            text: Raw text containing exterior hazards.

        Returns:
            List of ObservationSchema objects.

        Raises:
            ValueError: If text is empty.
            LangChainException: If OpenAI API fails.

        """
        if not text.strip():
            raise ValueError('Exterior text cannot be empty')

        try:
            observations = await parse_exterior_text_async(text)
            logger.info(f'Parsed {len(observations)} exterior observations')
            return observations
        except LangChainException:
            logger.exception('OpenAI API error during exterior parsing')
            raise

    def parse_interior(
        self,
        text: str,
        unit_name: str | None = None,
    ) -> list[ObservationSchema]:
        """Parse interior hazards text (sync).

        Args:
            text: Raw text containing interior hazards.
            unit_name: Optional unit name when text describes a single unit.

        Returns:
            List of ObservationSchema objects.

        Raises:
            ValueError: If text is empty.
            LangChainException: If OpenAI API fails.

        """
        if not text.strip():
            raise ValueError('Interior text cannot be empty')

        try:
            observations = parse_interior_text(text)
            if unit_name:
                for obs in observations:
                    obs.unit = unit_name
            logger.info(f'Parsed {len(observations)} interior observations')
            return observations
        except LangChainException:
            logger.exception('OpenAI API error during interior parsing')
            raise

    async def parse_interior_async(
        self,
        text: str,
        unit_name: str | None = None,
    ) -> list[ObservationSchema]:
        """Parse interior hazards text (async).

        Args:
            text: Raw text containing interior hazards.
            unit_name: Optional unit name when text describes a single unit.

        Returns:
            List of ObservationSchema objects.

        Raises:
            ValueError: If text is empty.
            LangChainException: If OpenAI API fails.

        """
        if not text.strip():
            raise ValueError('Interior text cannot be empty')

        try:
            observations = await parse_interior_text_async(text)
            if unit_name:
                for obs in observations:
                    obs.unit = unit_name
            logger.info(f'Parsed {len(observations)} interior observations')
            return observations
        except LangChainException:
            logger.exception('OpenAI API error during interior parsing')
            raise

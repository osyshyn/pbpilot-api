"""LLM configuration for Lead-Based Paint parsing."""

from typing import Any, cast

from langchain_openai import ChatOpenAI

from services.lead_paint.schemas import SectionExtractionSchema

_STRUCTURED_LLM: Any = None
_ASYNC_STRUCTURED_LLM: Any = None


def get_structured_llm() -> Any:
    """Get LLM with structured output for Lead Paint parsing (sync).

    API key is loaded from config.settings.Settings.

    Returns:
        ChatOpenAI instance with structured output bound to SectionExtractionSchema.

    Raises:
        ValueError: If OPENAI_API_KEY is not set.

    """
    global _STRUCTURED_LLM
    if _STRUCTURED_LLM is not None:
        return _STRUCTURED_LLM

    from config.settings import Settings

    settings = Settings.load()
    api_key = settings.openai_settings.API_KEY
    if not api_key:
        raise ValueError(
            'OPENAI_API_KEY is not set. '
            'Add OPENAI_API_KEY to your .env file.'
        )

    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0,
        api_key=cast(Any, api_key),
    )
    _STRUCTURED_LLM = llm.with_structured_output(SectionExtractionSchema)
    return _STRUCTURED_LLM


def get_async_structured_llm() -> Any:
    """Get async LLM with structured output for Lead Paint parsing.

    Same as get_structured_llm() but for async calls via .ainvoke().

    Returns:
        ChatOpenAI instance with structured output (use with ainvoke).

    """
    global _ASYNC_STRUCTURED_LLM
    if _ASYNC_STRUCTURED_LLM is not None:
        return _ASYNC_STRUCTURED_LLM

    from config.settings import Settings

    settings = Settings.load()
    api_key = settings.openai_settings.API_KEY
    if not api_key:
        raise ValueError(
            'OPENAI_API_KEY is not set. '
            'Add OPENAI_API_KEY to your .env file.'
        )

    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0,
        api_key=cast(Any, api_key),
    )
    _ASYNC_STRUCTURED_LLM = llm.with_structured_output(SectionExtractionSchema)
    return _ASYNC_STRUCTURED_LLM

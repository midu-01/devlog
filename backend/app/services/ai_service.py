"""LangChain AI layer: post summarization and auto-tagging.

Provider is configured via .env (LLM_PROVIDER / LLM_MODEL). Swapping providers
is a one-line change in .env thanks to LangChain's shared chat-model interface.
"""

import logging
from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger(__name__)

# Posts can be long; keep prompts inside free-tier context limits.
MAX_CONTENT_CHARS = 12_000


@lru_cache
def get_chat_model() -> BaseChatModel:
    """Build the chat model once. Swap provider via LLM_PROVIDER in .env."""
    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=settings.llm_model, api_key=settings.groq_api_key, temperature=0.3)
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI  # pip install langchain-openai

        return ChatOpenAI(model=settings.llm_model, temperature=0.3)
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic  # pip install langchain-anthropic

        return ChatAnthropic(model=settings.llm_model, temperature=0.3)
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider!r}")


# ---------- Summarization ----------

_summary_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You summarize blog posts. Write a 2-3 sentence TL;DR in plain prose. "
            "No preamble, no markdown, no 'This post is about' — just the summary.",
        ),
        ("human", "Summarize this blog post:\n\n{content}"),
    ]
)


def summarize_post(content: str) -> str:
    """Return a 2-3 sentence TL;DR of the post content."""
    chain = _summary_prompt | get_chat_model()
    result = chain.invoke({"content": content[:MAX_CONTENT_CHARS]})
    return result.content.strip()


# ---------- Tag generation (structured output — parsing never breaks) ----------


class TagList(BaseModel):
    """Schema the LLM must fill; enforced by with_structured_output."""

    tags: list[str] = Field(
        min_length=3,
        max_length=5,
        description="3-5 relevant topic tags: lowercase, single words or short phrases",
    )


_tags_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You generate topic tags for blog posts. Return 3-5 tags: lowercase, "
            "single words or short phrases (max 3 words), no '#' prefix, no duplicates.",
        ),
        ("human", "Generate tags for this blog post:\n\n{content}"),
    ]
)


def generate_tags(content: str) -> list[str]:
    """Return 3-5 lowercase topic tags for the post content."""
    chain = _tags_prompt | get_chat_model().with_structured_output(TagList)
    result: TagList = chain.invoke({"content": content[:MAX_CONTENT_CHARS]})
    # Normalize defensively even though the prompt asks for lowercase
    seen: set[str] = set()
    tags = []
    for tag in result.tags:
        clean = tag.strip().lower().lstrip("#")[:50]
        if clean and clean not in seen:
            seen.add(clean)
            tags.append(clean)
    return tags[:5]

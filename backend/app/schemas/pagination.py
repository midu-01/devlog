from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated response: {"items": [...], "total": N, "limit": X, "offset": Y}."""

    items: list[T]
    total: int
    limit: int
    offset: int

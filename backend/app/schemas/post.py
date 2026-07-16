from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthorRead(BaseModel):
    """Minimal public author info nested inside post responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10)


class PostUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10)


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author: AuthorRead
    summary: str | None = None
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime

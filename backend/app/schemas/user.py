from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt caps input at 72 bytes
    bio: str | None = None


class UserRead(BaseModel):
    """Public user representation — never includes the password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    bio: str | None
    created_at: datetime

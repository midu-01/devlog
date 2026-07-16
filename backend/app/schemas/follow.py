from pydantic import BaseModel, ConfigDict


class UserSummary(BaseModel):
    """Public snippet of a user for follower/following lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    bio: str | None = None

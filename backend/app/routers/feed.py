from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.pagination import Pagination
from app.database import get_db
from app.models.user import User
from app.schemas.pagination import Page
from app.schemas.post import PostRead
from app.services import follow_service

router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.get("", response_model=Page[PostRead])
def read_feed(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Pagination,
) -> Page[PostRead]:
    posts, total = follow_service.get_feed(db, current_user, page.limit, page.offset)
    return Page(
        items=[PostRead.model_validate(p) for p in posts],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )

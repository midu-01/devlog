from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.pagination import Pagination
from app.database import get_db
from app.models.user import User
from app.schemas.follow import UserSummary
from app.schemas.pagination import Page
from app.schemas.post import PostRead
from app.schemas.user import UserRead
from app.services import follow_service, post_service

router = APIRouter(prefix="/api/users", tags=["users"])

DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: CurrentUser) -> UserRead:
    return current_user


@router.get("/{username}/posts", response_model=Page[PostRead])
def read_user_posts(username: str, db: DB, page: Pagination) -> Page[PostRead]:
    author = follow_service.get_user_by_username(db, username)
    posts, total = post_service.list_posts_by_user(db, author, page.limit, page.offset)
    return Page(
        items=[PostRead.model_validate(p) for p in posts],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )


@router.post("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow(username: str, db: DB, current_user: CurrentUser) -> None:
    follow_service.follow_user(db, current_user, username)


@router.delete("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow(username: str, db: DB, current_user: CurrentUser) -> None:
    follow_service.unfollow_user(db, current_user, username)


@router.get("/{username}/followers", response_model=Page[UserSummary])
def read_followers(username: str, db: DB, page: Pagination) -> Page[UserSummary]:
    users, total = follow_service.list_followers(db, username, page.limit, page.offset)
    return Page(
        items=[UserSummary.model_validate(u) for u in users],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{username}/following", response_model=Page[UserSummary])
def read_following(username: str, db: DB, page: Pagination) -> Page[UserSummary]:
    users, total = follow_service.list_following(db, username, page.limit, page.offset)
    return Page(
        items=[UserSummary.model_validate(u) for u in users],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.pagination import Pagination
from app.database import get_db
from app.models.user import User
from app.schemas.pagination import Page
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.services import post_service

router = APIRouter(prefix="/api/posts", tags=["posts"])

DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    background_tasks: BackgroundTasks,
    db: DB,
    current_user: CurrentUser,
) -> PostRead:
    post = post_service.create_post(db, current_user, post_in)
    # AI enrichment runs AFTER the response is sent; never blocks or fails creation
    background_tasks.add_task(post_service.enrich_post_ai, post.id)
    return post


# NOTE: must be declared before /{post_id}, or "search" would match the int path param
@router.get("/search", response_model=Page[PostRead])
def search_posts(
    db: DB,
    page: Pagination,
    tag: Annotated[str, Query(min_length=1, max_length=50)],
) -> Page[PostRead]:
    posts, total = post_service.search_posts_by_tag(db, tag, page.limit, page.offset)
    return Page(
        items=[PostRead.model_validate(p) for p in posts],
        total=total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, db: DB) -> PostRead:
    return post_service.get_post(db, post_id)


@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int, post_in: PostUpdate, db: DB, current_user: CurrentUser
) -> PostRead:
    return post_service.update_post(db, post_id, current_user, post_in)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: DB, current_user: CurrentUser) -> None:
    post_service.delete_post(db, post_id, current_user)


@router.post("/{post_id}/regenerate-ai", status_code=status.HTTP_202_ACCEPTED)
def regenerate_ai(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: DB,
    current_user: CurrentUser,
) -> dict[str, str]:
    post_service.trigger_regenerate_ai(db, post_id, current_user)  # 403/404/429 checks
    background_tasks.add_task(post_service.enrich_post_ai, post_id)
    return {"status": "queued"}

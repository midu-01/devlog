import logging
import time

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from app.services import ai_service

logger = logging.getLogger(__name__)


def create_post(db: Session, author: User, post_in: PostCreate) -> Post:
    post = Post(title=post_in.title, content=post_in.content, author_id=author.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_post(db: Session, post_id: int) -> Post:
    post = db.scalar(
        select(Post).options(joinedload(Post.author)).where(Post.id == post_id)
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def _require_owner(post: Post, user: User) -> None:
    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this post",
        )


def update_post(db: Session, post_id: int, user: User, post_in: PostUpdate) -> Post:
    post = get_post(db, post_id)
    _require_owner(post, user)
    post.title = post_in.title
    post.content = post_in.content
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int, user: User) -> None:
    post = get_post(db, post_id)
    _require_owner(post, user)
    db.delete(post)
    db.commit()


def list_posts_by_user(
    db: Session, author: User, limit: int, offset: int
) -> tuple[list[Post], int]:
    total = db.scalar(select(func.count()).select_from(Post).where(Post.author_id == author.id))
    posts = list(
        db.scalars(
            select(Post)
            .options(joinedload(Post.author))
            .where(Post.author_id == author.id)
            .order_by(Post.created_at.desc(), Post.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return posts, total or 0


def search_posts_by_tag(db: Session, tag: str, limit: int, offset: int) -> tuple[list[Post], int]:
    """Posts whose tags array contains `tag` (exact match, case-insensitive via lowering input)."""
    condition = Post.tags.contains([tag.strip().lower()])
    total = db.scalar(select(func.count()).select_from(Post).where(condition))
    posts = list(
        db.scalars(
            select(Post)
            .options(joinedload(Post.author))
            .where(condition)
            .order_by(Post.created_at.desc(), Post.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return posts, total or 0


# ---------- AI enrichment (runs in BackgroundTasks, after the response is sent) ----------

def enrich_post_ai(post_id: int) -> None:
    """Generate summary + tags for a post and persist them.

    Runs as a FastAPI background task AFTER the response is sent, so it must
    open its own DB session (the request session is closed by then) and must
    never raise — on any failure we log and leave summary/tags null.
    """
    db = SessionLocal()
    try:
        post = db.get(Post, post_id)
        if post is None:  # deleted before the task ran
            return
        content = post.content
    finally:
        db.close()

    summary: str | None = None
    tags: list[str] | None = None
    try:
        summary = ai_service.summarize_post(content)
    except Exception:
        logger.exception("Summary generation failed for post %s", post_id)
    try:
        tags = ai_service.generate_tags(content)
    except Exception:
        logger.exception("Tag generation failed for post %s", post_id)

    if summary is None and tags is None:
        return  # nothing to write; post stays as-is

    db = SessionLocal()
    try:
        post = db.get(Post, post_id)
        if post is None:
            return
        if summary is not None:
            post.summary = summary
        if tags is not None:
            post.tags = tags
        db.commit()
        logger.info("AI enrichment done for post %s", post_id)
    finally:
        db.close()


# In-memory rate guard for regenerate-ai: post_id -> last trigger monotonic time.
# LIMITATION: per-process only. With multiple uvicorn workers each has its own
# dict, and it resets on restart. Production: Redis with SET NX EX, or a proper
# rate limiter (slowapi). Fine for a single-process dev server.
_REGEN_COOLDOWN_SECONDS = 60.0
_last_regen: dict[int, float] = {}


def trigger_regenerate_ai(db: Session, post_id: int, user: User) -> None:
    """Validate ownership + cooldown; actual work is queued by the router."""
    post = get_post(db, post_id)
    _require_owner(post, user)

    now = time.monotonic()
    last = _last_regen.get(post_id)
    if last is not None and now - last < _REGEN_COOLDOWN_SECONDS:
        retry_in = int(_REGEN_COOLDOWN_SECONDS - (now - last)) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"AI regeneration is rate-limited; retry in {retry_in}s",
        )
    _last_regen[post_id] = now

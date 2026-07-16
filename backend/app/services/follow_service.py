from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.follow import Follow
from app.models.post import Post
from app.models.user import User


def get_user_by_username(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def follow_user(db: Session, follower: User, username: str) -> None:
    target = get_user_by_username(db, username)
    if target.id == follower.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself"
        )
    existing = db.get(Follow, (follower.id, target.id))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Already following {username}",
        )
    db.add(Follow(follower_id=follower.id, followed_id=target.id))
    db.commit()


def unfollow_user(db: Session, follower: User, username: str) -> None:
    target = get_user_by_username(db, username)
    follow = db.get(Follow, (follower.id, target.id))
    if follow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"You are not following {username}",
        )
    db.delete(follow)
    db.commit()


def list_followers(
    db: Session, username: str, limit: int, offset: int
) -> tuple[list[User], int]:
    target = get_user_by_username(db, username)
    base = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.followed_id == target.id)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery()))
    users = list(
        db.scalars(base.order_by(Follow.created_at.desc()).limit(limit).offset(offset))
    )
    return users, total or 0


def list_following(
    db: Session, username: str, limit: int, offset: int
) -> tuple[list[User], int]:
    target = get_user_by_username(db, username)
    base = (
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.follower_id == target.id)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery()))
    users = list(
        db.scalars(base.order_by(Follow.created_at.desc()).limit(limit).offset(offset))
    )
    return users, total or 0


def get_feed(db: Session, user: User, limit: int, offset: int) -> tuple[list[Post], int]:
    """Posts authored by users that `user` follows, newest first."""
    followed_ids = select(Follow.followed_id).where(Follow.follower_id == user.id)

    total = db.scalar(
        select(func.count()).select_from(Post).where(Post.author_id.in_(followed_ids))
    )
    posts = list(
        db.scalars(
            select(Post)
            .options(joinedload(Post.author))
            .where(Post.author_id.in_(followed_ids))
            .order_by(Post.created_at.desc(), Post.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return posts, total or 0

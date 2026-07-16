from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user. Raises 409 if username or email is already taken."""
    if db.scalar(select(User).where(User.username == user_in.username)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    if db.scalar(select(User).where(User.email == user_in.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        bio=user_in.bio,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> str:
    """Verify credentials and return a JWT. Raises 401 on failure."""
    user = db.scalar(select(User).where(User.username == username))
    # Same error for unknown user and wrong password — don't leak which one failed.
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(subject=str(user.id))


def get_user_by_id(db: Session, user_id: int) -> User:
    """Fetch a user by id. Raises 404 if not found."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

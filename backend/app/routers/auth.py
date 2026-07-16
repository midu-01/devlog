from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserRead:
    user = auth_service.register_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    access_token = auth_service.authenticate_user(db, form_data.username, form_data.password)
    return Token(access_token=access_token)

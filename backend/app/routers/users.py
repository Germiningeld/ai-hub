from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.db.models import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services import user_service

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_in: UserCreate,
        db: Session = Depends(get_db)
) -> Any:
    """
    Создает нового пользователя.
    """
    # Проверяем, существует ли пользователь с таким email
    if user_service.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован",
        )
    # Проверяем, существует ли пользователь с таким username
    if user_service.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже занято",
        )

    # Создаем пользователя
    user = user_service.create_user(db, user_in)
    return user


@router.get("/me", response_model=UserSchema)
async def read_current_user(
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получает информацию о текущем пользователе.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user(
        user_in: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Any:
    """
    Обновляет информацию о текущем пользователе.
    """
    # Проверяем, существует ли пользователь с таким email (если email обновляется)
    if user_in.email and user_in.email != current_user.email:
        if user_service.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже зарегистрирован",
            )

    # Проверяем, существует ли пользователь с таким username (если username обновляется)
    if user_in.username and user_in.username != current_user.username:
        if user_service.get_by_username(db, username=user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя уже занято",
            )

    # Обновляем пользователя
    updated_user = user_service.update_user(db, current_user.id, user_in)
    return updated_user
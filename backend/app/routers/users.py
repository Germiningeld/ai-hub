from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm
from app.schemas.user import UserSchema, UserCreateSchema, UserUpdateSchema
from app.services import user_service

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_in: UserCreateSchema,
        db: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Создает нового пользователя.
    """
    # Проверяем, существует ли пользователь с таким email
    if await user_service.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован",
        )
    # Проверяем, существует ли пользователь с таким username
    if await user_service.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже занято",
        )

    # Создаем пользователя
    user = await user_service.create_user(db, user_in)
    return user


@router.get("/me", response_model=UserSchema)
async def read_current_user(
        current_user: UserOrm = Depends(get_current_user)
) -> Any:
    """
    Получает информацию о текущем пользователе.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user(
        user_in: UserUpdateSchema,
        current_user: UserOrm = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Обновляет информацию о текущем пользователе.
    """
    # Проверяем, существует ли пользователь с таким email (если email обновляется)
    if user_in.email and user_in.email != current_user.email:
        if await user_service.get_by_email(db, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже зарегистрирован",
            )

    # Проверяем, существует ли пользователь с таким username (если username обновляется)
    if user_in.username and user_in.username != current_user.username:
        if await user_service.get_by_username(db, username=user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя уже занято",
            )

    # Обновляем пользователя
    updated_user = await user_service.update_user(db, current_user.id, user_in)
    return updated_user
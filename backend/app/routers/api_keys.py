from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, ApiKeyOrm
from app.schemas.api_key import ApiKeyCreateSchema, ApiKeyResponseSchema, ApiKeyUpdateSchema

router = APIRouter()


@router.get("/", response_model=List[ApiKeyResponseSchema])
async def get_api_keys(
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Получает список API ключей текущего пользователя.
    """
    result = await db.execute(
        select(ApiKeyOrm).where(ApiKeyOrm.user_id == current_user.id)
    )
    api_keys = result.scalars().all()

    # FastAPI автоматически преобразует ORM-объекты в модели Pydantic
    return api_keys


@router.post("/", response_model=ApiKeyResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_api_key(
        api_key: ApiKeyCreateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Создает новый API ключ для текущего пользователя.
    """
    # Проверяем уникальность ключа
    result = await db.execute(
        ApiKeyOrm.__table__.select().where(
            (ApiKeyOrm.user_id == current_user.id) &
            (ApiKeyOrm.provider == api_key.provider) &
            (ApiKeyOrm.api_key == api_key.api_key)
        )
    )
    existing_key = result.scalar_one_or_none()

    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API ключ с такими параметрами уже существует"
        )

    # Создаем новый ключ
    db_api_key = ApiKeyOrm(
        user_id=current_user.id,
        provider=api_key.provider,
        api_key=api_key.api_key,
        name=api_key.name,
        is_active=api_key.is_active
    )

    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)

    return db_api_key


@router.put("/{key_id}", response_model=ApiKeyResponseSchema)
async def update_api_key(
        key_id: int,
        api_key: ApiKeyUpdateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Обновляет существующий API ключ.
    """
    # Находим ключ
    result = await db.execute(
        select(ApiKeyOrm).where(
            (ApiKeyOrm.id == key_id) &
            (ApiKeyOrm.user_id == current_user.id)
        )
    )
    db_api_key = result.scalar_one_or_none()

    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API ключ не найден"
        )

    # Обновляем поля
    if api_key.name is not None:
        db_api_key.name = api_key.name

    if api_key.is_active is not None:
        db_api_key.is_active = api_key.is_active

    # Обновляем сам ключ, только если он предоставлен
    if api_key.api_key:
        db_api_key.api_key = api_key.api_key

    await db.commit()
    await db.refresh(db_api_key)

    return db_api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
        key_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет API ключ.
    """
    # Находим ключ
    result = await db.execute(
        select(ApiKeyOrm).where(
            (ApiKeyOrm.id == key_id) &
            (ApiKeyOrm.user_id == current_user.id)
        )
    )
    db_api_key = result.scalar_one_or_none()

    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API ключ не найден"
        )

    # Удаляем ключ
    await db.delete(db_api_key)
    await db.commit()

    return None

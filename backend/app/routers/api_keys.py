from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core import get_current_user
from app.db.session import get_db
from app.db.models import User, ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyUpdate

router = APIRouter()


@router.get("/", response_model=List[ApiKeyResponse])
async def get_api_keys(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получает список API ключей текущего пользователя.
    """
    return db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()


@router.post("/", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
        api_key: ApiKeyCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Создает новый API ключ для текущего пользователя.
    """
    # Проверяем уникальность ключа
    existing_key = db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.provider == api_key.provider,
        ApiKey.api_key == api_key.api_key
    ).first()

    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API ключ с такими параметрами уже существует"
        )

    # Создаем новый ключ
    db_api_key = ApiKey(
        user_id=current_user.id,
        provider=api_key.provider,
        api_key=api_key.api_key,
        name=api_key.name,
        is_active=api_key.is_active
    )

    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)

    return db_api_key


@router.put("/{key_id}", response_model=ApiKeyResponse)
async def update_api_key(
        key_id: int,
        api_key: ApiKeyUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Обновляет существующий API ключ.
    """
    # Находим ключ
    db_api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()

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

    db.commit()
    db.refresh(db_api_key)

    return db_api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
        key_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Удаляет API ключ.
    """
    # Находим ключ
    db_api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()

    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API ключ не найден"
        )

    # Удаляем ключ
    db.delete(db_api_key)
    db.commit()

    return None
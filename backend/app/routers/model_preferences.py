from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Dict

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, ModelPreferencesOrm, ApiKeyOrm, ProviderOrm, AIModelOrm
from app.schemas.model_preferences import (
    ModelPreferencesSchema,
    ModelPreferencesCreateSchema,
    ModelPreferencesUpdateSchema,
    AvailableModelSchema,
    AvailableModelsResponseSchema
)
from app.services import ai_service_factory

router = APIRouter()


@router.get("/available", response_model=AvailableModelsResponseSchema)
async def get_available_models(
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает список доступных моделей из всех настроенных провайдеров.
    """
    # Получаем список API ключей пользователя
    result = await db.execute(
        select(ApiKeyOrm).filter(
            (ApiKeyOrm.user_id == current_user.id) &
            (ApiKeyOrm.is_active == True)
        )
    )
    api_keys = result.scalars().all()

    providers = [key.provider for key in api_keys]
    available_models = []

    # Запрашиваем модели для каждого провайдера
    for provider in providers:
        try:
            ai_service = await ai_service_factory.create_service_for_user(
                db, current_user.id, provider
            )

            if ai_service:
                provider_models = await ai_service.get_available_models()
                available_models.extend(provider_models)
        except Exception as e:
            # Логируем ошибку, но продолжаем для других провайдеров
            print(f"Ошибка при получении моделей от {provider}: {str(e)}")
            continue

    return {"models": available_models}


@router.get("/preferences", response_model=List[ModelPreferencesSchema])
async def get_model_preferences(
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает список настроек моделей пользователя.
    """
    result = await db.execute(
        select(ModelPreferencesOrm)
        .filter(ModelPreferencesOrm.user_id == current_user.id)
        .order_by(ModelPreferencesOrm.provider_id, ModelPreferencesOrm.model_id)
    )
    preferences = result.scalars().all()

    return preferences


@router.get("/preferences/default", response_model=Dict[int, ModelPreferencesSchema])
async def get_default_preferences(
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает настройки моделей по умолчанию для каждого провайдера.
    """
    result = await db.execute(
        select(ModelPreferencesOrm).filter(
            (ModelPreferencesOrm.user_id == current_user.id) &
            (ModelPreferencesOrm.is_default == True)
        )
    )
    defaults = result.scalars().all()

    result = {}
    for pref in defaults:
        result[pref.provider_id] = ModelPreferencesSchema.from_orm(pref)

    return result


@router.post("/preferences", response_model=ModelPreferencesSchema, status_code=status.HTTP_201_CREATED)
async def create_model_preferences(
        preferences_data: ModelPreferencesCreateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Создает новые настройки модели.
    """
    # Проверяем, существуют ли провайдер и модель
    provider_result = await db.execute(
        select(ProviderOrm).filter(ProviderOrm.id == preferences_data.provider_id)
    )
    provider = provider_result.scalar_one_or_none()

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Провайдер с ID {preferences_data.provider_id} не найден"
        )

    model_result = await db.execute(
        select(AIModelOrm).filter(
            (AIModelOrm.id == preferences_data.model_id) &
            (AIModelOrm.provider_id == preferences_data.provider_id)
        )
    )
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Модель с ID {preferences_data.model_id} для провайдера с ID {preferences_data.provider_id} не найдена"
        )

    # Проверяем, существуют ли уже настройки для данной модели
    result = await db.execute(
        select(ModelPreferencesOrm).filter(
            (ModelPreferencesOrm.user_id == current_user.id) &
            (ModelPreferencesOrm.provider_id == preferences_data.provider_id) &
            (ModelPreferencesOrm.model_id == preferences_data.model_id)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Настройки для этой модели уже существуют"
        )

    # Если это настройки по умолчанию, сбрасываем другие настройки по умолчанию для этого провайдера
    if preferences_data.is_default:
        await db.execute(
            update(ModelPreferencesOrm)
            .where(
                (ModelPreferencesOrm.user_id == current_user.id) &
                (ModelPreferencesOrm.provider_id == preferences_data.provider_id) &
                (ModelPreferencesOrm.is_default == True)
            )
            .values(is_default=False)
        )

    # Создаем новые настройки
    new_preferences = ModelPreferencesOrm(
        user_id=current_user.id,
        provider_id=preferences_data.provider_id,
        model_id=preferences_data.model_id,
        max_tokens=preferences_data.max_tokens,
        temperature=preferences_data.temperature,
        system_prompt=preferences_data.system_prompt,
        is_default=preferences_data.is_default
    )

    db.add(new_preferences)
    await db.commit()
    await db.refresh(new_preferences)

    return new_preferences


@router.put("/preferences/{preferences_id}", response_model=ModelPreferencesSchema)
async def update_model_preferences(
        preferences_id: int,
        preferences_data: ModelPreferencesUpdateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Обновляет настройки модели.
    """
    result = await db.execute(
        select(ModelPreferencesOrm).filter(
            (ModelPreferencesOrm.id == preferences_id) &
            (ModelPreferencesOrm.user_id == current_user.id)
        )
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки модели не найдены"
        )

    # Проверяем валидность provider_id и model_id, если они изменяются
    if preferences_data.provider_id is not None:
        provider_result = await db.execute(
            select(ProviderOrm).filter(ProviderOrm.id == preferences_data.provider_id)
        )
        provider = provider_result.scalar_one_or_none()

        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Провайдер с ID {preferences_data.provider_id} не найден"
            )

        preferences.provider_id = preferences_data.provider_id

    if preferences_data.model_id is not None:
        model_result = await db.execute(
            select(AIModelOrm).filter(
                (AIModelOrm.id == preferences_data.model_id) &
                (AIModelOrm.provider_id == (preferences_data.provider_id or preferences.provider_id))
            )
        )
        model = model_result.scalar_one_or_none()

        if not model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Модель с ID {preferences_data.model_id} для выбранного провайдера не найдена"
            )

        preferences.model_id = preferences_data.model_id

    # Обновляем поля настроек
    if preferences_data.max_tokens is not None:
        preferences.max_tokens = preferences_data.max_tokens

    if preferences_data.temperature is not None:
        preferences.temperature = preferences_data.temperature

    if preferences_data.system_prompt is not None:
        preferences.system_prompt = preferences_data.system_prompt

    # Если устанавливаем is_default в True, сбрасываем другие настройки по умолчанию для этого провайдера
    if preferences_data.is_default is True and not preferences.is_default:
        await db.execute(
            update(ModelPreferencesOrm)
            .where(
                (ModelPreferencesOrm.user_id == current_user.id) &
                (ModelPreferencesOrm.provider_id == preferences.provider_id) &
                (ModelPreferencesOrm.is_default == True) &
                (ModelPreferencesOrm.id != preferences_id)
            )
            .values(is_default=False)
        )

    if preferences_data.is_default is not None:
        preferences.is_default = preferences_data.is_default

    await db.commit()
    await db.refresh(preferences)

    return preferences

@router.delete("/preferences/{preferences_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_preferences(
        preferences_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет настройки модели.
    """
    result = await db.execute(
        select(ModelPreferencesOrm).filter(
            (ModelPreferencesOrm.id == preferences_id) &
            (ModelPreferencesOrm.user_id == current_user.id)
        )
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки модели не найдены"
        )

    # Если удаляем настройки по умолчанию, нужно назначить другие настройки по умолчанию
    if preferences.is_default:
        # Находим другую модель для этого провайдера
        result = await db.execute(
            select(ModelPreferencesOrm).filter(
                (ModelPreferencesOrm.user_id == current_user.id) &
                (ModelPreferencesOrm.provider == preferences.provider) &
                (ModelPreferencesOrm.id != preferences_id)
            )
        )
        other_model = result.scalar_one_or_none()

        if other_model:
            other_model.is_default = True
            db.add(other_model)

    await db.delete(preferences)
    await db.commit()

    return None
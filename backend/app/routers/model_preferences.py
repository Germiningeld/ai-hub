from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Dict

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, ModelPreferencesOrm, ApiKeyOrm
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
        .order_by(ModelPreferencesOrm.provider, ModelPreferencesOrm.model)
    )
    preferences = result.scalars().all()

    return preferences


@router.get("/preferences/default", response_model=Dict[str, ModelPreferencesSchema])
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
        result[pref.provider] = ModelPreferencesSchema.from_orm(pref)

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
    # Проверяем API-ключ
    api_key = await db.get(ApiKeyOrm, preferences_data.api_key_id)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API ключ не найден")

    # Проверяем, существуют ли уже настройки с такой же моделью для данного API-ключа
    result = await db.execute(
        select(ModelPreferencesOrm).filter(
            (ModelPreferencesOrm.user_id == current_user.id) &
            (ModelPreferencesOrm.api_key_id == preferences_data.api_key_id) &
            (ModelPreferencesOrm.model == preferences_data.model)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Настройки для этой модели с данным API-ключом уже существуют"
        )

    # Если новая настройка устанавливается как дефолтная
    if preferences_data.is_default:
        # Находим и сбрасываем все другие дефолтные настройки для того же API-ключа
        await db.execute(
            update(ModelPreferencesOrm)
            .where(
                (ModelPreferencesOrm.user_id == current_user.id) &
                (ModelPreferencesOrm.api_key_id == preferences_data.api_key_id) &
                (ModelPreferencesOrm.is_default == True)
            )
            .values(is_default=False)
        )

    # Создаем новые настройки
    new_preferences = ModelPreferencesOrm(
        user_id=current_user.id,
        provider=api_key.provider,  # Берем провайдера из API-ключа
        api_key_id=preferences_data.api_key_id,
        model=preferences_data.model,
        max_tokens=preferences_data.max_tokens,
        temperature=preferences_data.temperature,
        system_prompt=preferences_data.system_prompt,
        is_default=preferences_data.is_default,
        input_cost=preferences_data.input_cost,
        output_cost=preferences_data.output_cost,
        cached_input_cost=preferences_data.cached_input_cost,
        description=preferences_data.description,
        use_count=0,
        last_used_at=None
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

    # Проверяем API-ключ, если он передан
    if preferences_data.api_key_id is not None:
        api_key = await db.get(ApiKeyOrm, preferences_data.api_key_id)
        if not api_key or api_key.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="API ключ не найден")

    # Если устанавливаем is_default в True, сбрасываем другие настройки по умолчанию для этого API-ключа
    if preferences_data.is_default is True and not preferences.is_default:
        await db.execute(
            update(ModelPreferencesOrm)
            .where(
                (ModelPreferencesOrm.user_id == current_user.id) &
                (ModelPreferencesOrm.api_key_id == preferences.api_key_id) &
                (ModelPreferencesOrm.is_default == True) &
                (ModelPreferencesOrm.id != preferences_id)
            )
            .values(is_default=False)
        )

    # Обновляем поля настроек
    if preferences_data.api_key_id is not None:
        preferences.api_key_id = preferences_data.api_key_id

    if preferences_data.max_tokens is not None:
        preferences.max_tokens = preferences_data.max_tokens

    if preferences_data.temperature is not None:
        preferences.temperature = preferences_data.temperature

    if preferences_data.system_prompt is not None:
        preferences.system_prompt = preferences_data.system_prompt

    if preferences_data.is_default is not None:
        preferences.is_default = preferences_data.is_default

    # Обновляем поля стоимости
    if preferences_data.input_cost is not None:
        preferences.input_cost = preferences_data.input_cost

    if preferences_data.output_cost is not None:
        preferences.output_cost = preferences_data.output_cost

    if preferences_data.cached_input_cost is not None:
        preferences.cached_input_cost = preferences_data.cached_input_cost

    if preferences_data.description is not None:
        preferences.description = preferences_data.description

    # Устанавливаем use_count и last_used_at по умолчанию, если они не были установлены
    preferences.use_count = preferences.use_count or 0

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

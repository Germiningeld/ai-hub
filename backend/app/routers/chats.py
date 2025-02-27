from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.dependencies import get_current_user, get_db
from app.db.models import User
from app.schemas.chat import (
    CompletionRequest,
    CompletionResponse,
    TokenCountRequest,
    TokenCountResponse,
    ErrorResponse
)
from app.services import ai_service_factory

router = APIRouter()


@router.post(
    "/completion",
    response_model=CompletionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def generate_completion(
        request: CompletionRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Генерирует ответ на основе запроса пользователя.
    """
    # Создаем сервис AI для указанного провайдера
    ai_service = await ai_service_factory.create_service_for_user(
        db, current_user.id, request.provider
    )

    if not ai_service:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "error_message": f"API ключ для провайдера {request.provider} не найден",
                "error_type": "api_key_not_found"
            }
        )

    # Генерируем ответ
    result = await ai_service.generate_completion(
        prompt=request.prompt,
        model=request.model,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        system_prompt=request.system_prompt
    )

    # Проверяем наличие ошибки
    if result.get("error", False):
        raise HTTPException(
            status_code=500 if result.get("error_type") != "api_key_not_found" else 400,
            detail=result
        )

    # Обновляем статистику использования в фоновом режиме
    background_tasks.add_task(
        ai_service.update_usage_statistics,
        db=db,
        user_id=current_user.id,
        tokens_data=result["tokens"],
        model=request.model,
        cost=result["cost"]
    )

    return result


@router.post(
    "/token-count",
    response_model=TokenCountResponse
)
async def count_tokens(
        request: TokenCountRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Подсчитывает количество токенов в тексте.
    """
    # Создаем сервис AI для указанного провайдера
    ai_service = await ai_service_factory.create_service_for_user(
        db, current_user.id, request.provider
    )

    if not ai_service:
        raise HTTPException(
            status_code=400,
            detail=f"API ключ для провайдера {request.provider} не найден"
        )

    # Подсчитываем токены
    result = await ai_service.calculate_tokens(
        text=request.text,
        model=request.model
    )

    return result
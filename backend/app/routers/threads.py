import json
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, MessageOrm, ThreadOrm, ProviderOrm, AIModelOrm, ModelPreferencesOrm
from app.schemas.thread import (
    ThreadCreateSchema, ThreadUpdateSchema, ThreadSchema,
    ThreadSummarySchema, ThreadListParamsSchema, BulkThreadActionSchema,
    MessageCreateSchema, MessageSchema, SendMessageRequestSchema,
    CompletionRequestSchema, CompletionResponseSchema, TokenCountRequestSchema,
    TokenCountResponseSchema, ErrorResponseSchema
)
from app.services.thread_service import ThreadService, ThreadNotFoundException, AccessDeniedException, \
    CategoryNotFoundException
from app.services.message_service import MessageService, MessageServiceException
from app.services.ai_service_factory import AIServiceFactory, APIKeyNotFoundException

router = APIRouter()


@router.post("/", response_model=ThreadSchema, status_code=status.HTTP_201_CREATED)
async def create_thread(
        thread_data: ThreadCreateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Создает новый тред и по желанию добавляет первое сообщение.
    """
    try:
        # Используем ThreadService для создания треда
        thread, messages = await ThreadService.create_thread(
            db=db,
            user_id=current_user.id,
            thread_data=thread_data
        )

        # Получаем категорию, если она есть
        category = None
        if thread.category_id:
            category = await ThreadService.get_category_by_id(db, thread.category_id)

        # Создаем структуру ответа
        response = {
            "id": thread.id,
            "user_id": thread.user_id,
            "title": thread.title,
            "provider_id": thread.provider_id,
            "model_id": thread.model_id,
            "provider_code": thread.provider_code,
            "model_code": thread.model_code,
            "category_id": thread.category_id,
            "is_pinned": thread.is_pinned,
            "is_archived": thread.is_archived,
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
            "last_message_at": thread.last_message_at,
            "message_count": len(messages),
            "category": category.__dict__ if category else None,
            "messages": []
        }

        # Добавляем сообщения в ответ
        for msg in messages:
            response["messages"].append({
                "id": msg.id,
                "thread_id": msg.thread_id,
                "role": msg.role,
                "content": msg.content,
                "tokens_total": msg.tokens_total,
                "model_id": msg.model_id,
                "provider_id": msg.provider_id,
                "model_code": msg.model_code,
                "provider_code": msg.provider_code,
                "meta_data": msg.meta_data if msg.meta_data else {},
                "created_at": msg.created_at
            })

        return ThreadSchema(**response)

    except CategoryNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании треда: {str(e)}"
        )


@router.post("/stream", status_code=status.HTTP_201_CREATED, response_class=StreamingResponse)
async def create_thread_stream(
        thread_data: ThreadCreateSchema,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Создает новый тред с первым сообщением и сразу получает потоковый ответ от нейросети.
    """
    # Проверяем, что есть начальное сообщение
    if not thread_data.initial_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для создания треда с потоковой генерацией необходимо начальное сообщение"
        )

    try:
        # Создаем тред с начальным сообщением
        thread, messages = await ThreadService.create_thread(
            db=db,
            user_id=current_user.id,
            thread_data=thread_data
        )

        # Функция генератор для потоковой передачи
        async def generate():
            try:
                # Отправляем информацию о созданном треде
                thread_info = {
                    "thread_id": thread.id,
                    "title": thread.title,
                    "provider_id": thread.provider_id,
                    "model_id": thread.model_id,
                    "provider_code": thread.provider_code,
                    "model_code": thread.model_code,
                    "messages": [
                        {
                            "id": msg.id,
                            "role": msg.role,
                            "content": msg.content,
                            "created_at": msg.created_at.isoformat()
                        } for msg in messages
                    ]
                }
                yield f"data: {json.dumps({'thread': thread_info})}\n\n"

                # Получаем пользовательское сообщение
                user_message = next((msg for msg in messages if msg.role == "user"), None)
                if not user_message:
                    error_message = "Сообщение пользователя не найдено"
                    yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"
                    return

                # Получаем системное сообщение если есть
                system_message = next((msg for msg in messages if msg.role == "system"), None)
                system_prompt = system_message.content if system_message else None

                # Получаем AI сервис для треда
                try:
                    # Используем тот же подход, что и в обычном create_thread
                    # Получаем информацию о треде
                    thread_result = await db.execute(
                        select(ThreadOrm).filter(ThreadOrm.id == thread.id)
                    )
                    thread_obj = thread_result.scalar_one_or_none()

                    if not thread_obj:
                        raise Exception(f"Тред с ID {thread.id} не найден")

                    # Создаем сервис AI для указанного провайдера
                    try:
                        ai_service = await AIServiceFactory.get_service_by_user_and_provider(
                            db, current_user.id, thread_obj.provider_id
                        )
                    except APIKeyNotFoundException:
                        error_message = f"API ключ для провайдера с ID {thread_obj.provider_id} не найден"
                        yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

                        # Сохраняем сообщение об ошибке в БД
                        await MessageService.save_error_message(
                            db=db,
                            thread_id=thread.id,
                            error_message=error_message,
                            error_type="api_key_not_found"
                        )
                        return
                    except Exception as e:
                        error_message = f"Ошибка при создании AI сервиса: {str(e)}"
                        yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

                        # Сохраняем сообщение об ошибке в БД
                        await MessageService.save_error_message(
                            db=db,
                            thread_id=thread.id,
                            error_message=error_message,
                            error_type="service_error"
                        )
                        return

                except Exception as e:
                    error_message = f"Ошибка при получении AI сервиса: {str(e)}"
                    yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

                    # Сохраняем сообщение об ошибке в БД
                    await MessageService.save_error_message(
                        db=db,
                        thread_id=thread.id,
                        error_message=error_message,
                        error_type="service_error"
                    )
                    return

                # Формируем контекст для запроса
                context = []
                if system_prompt:
                    context.append({"role": "system", "content": system_prompt})
                context.append({"role": "user", "content": user_message.content})

                # Определяем параметры для запроса
                max_tokens = thread_obj.max_tokens  # Используем max_tokens вместо max_completion_tokens
                temperature = thread_obj.temperature  # Значение по умолчанию

                # Генерируем ответ в потоковом режиме
                full_response = ""
                tokens_info = {}
                cost = 0

                # Используем метод generate_completion вместо stream_generation
                try:
                    # Генерируем ответ от ИИ с полным контекстом
                    result = await ai_service.generate_completion_with_context(
                        context=context,
                        model=thread_obj.model_code,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )

                    # Проверяем наличие ошибки
                    if result.get("error", False):
                        error_message = result.get("error_message", "Неизвестная ошибка при генерации ответа")
                        yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

                        # Сохраняем сообщение об ошибке в БД
                        await MessageService.save_error_message(
                            db=db,
                            thread_id=thread.id,
                            error_message=error_message,
                            error_type=result.get("error_type", "api_error"),
                            provider_id=thread_obj.provider_id,
                            model_id=thread_obj.model_id,
                            error_details=result
                        )
                        return

                    # Имитируем потоковую передачу одним куском (если настоящий стриминг не работает)
                    text = result.get("text", "")
                    if text:
                        # Отправляем текст клиенту
                        yield f"data: {json.dumps({'text': text})}\n\n"
                        full_response = text

                    # Получаем информацию о токенах и стоимости
                    tokens_info = result.get("tokens", {})
                    cost = result.get("cost", 0)

                except Exception as e:
                    error_message = f"Ошибка при генерации ответа: {str(e)}"
                    yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

                    # Сохраняем сообщение об ошибке в БД
                    await MessageService.save_error_message(
                        db=db,
                        thread_id=thread.id,
                        error_message=error_message,
                        error_type="api_error",
                        provider_id=thread_obj.provider_id,
                        model_id=thread_obj.model_id,
                        error_details=str(e)
                    )
                    return

                # Сохраняем ответ ассистента в БД, если он не пустой
                if full_response:
                    assistant_message = await MessageService.save_ai_response(
                        db=db,
                        thread_id=thread.id,
                        content=full_response,
                        model_id=thread_obj.model_id,
                        provider_id=thread_obj.provider_id,
                        tokens_data=tokens_info,
                        cost=cost,
                        meta_data={"with_context": True}
                    )

                    # Обновляем статистику использования в фоновом режиме
                    background_tasks.add_task(
                        ai_service.update_usage_statistics,
                        db=db,
                        user_id=current_user.id,
                        tokens_data=tokens_info,
                        model=thread_obj.model_code,
                        cost=cost
                    )

                    # Отправляем финальное сообщение с ID сохраненного сообщения
                    yield f"data: {json.dumps({'done': True, 'message_id': assistant_message.id})}\n\n"

            except Exception as e:
                # Обработка ошибок
                error_message = f"Ошибка при генерации ответа: {str(e)}"
                yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

                # Сохраняем сообщение об ошибке в БД
                await MessageService.save_error_message(
                    db=db,
                    thread_id=thread.id,
                    error_message=error_message,
                    error_type="api_error",
                    provider_id=thread.provider_id,
                    model_id=thread.model_id,
                    error_details=str(e)
                )

        # Возвращаем стрим-ответ с правильными заголовками
        headers = {
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream'
        }
        return StreamingResponse(generate(), headers=headers)

    except CategoryNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании треда: {str(e)}"
        )


@router.get("/", response_model=List[ThreadSummarySchema])
async def get_threads(
        params: ThreadListParamsSchema = Depends(),
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает список тредов пользователя с пагинацией и фильтрацией.
    """
    try:
        # Получаем треды с использованием ThreadService
        threads = await ThreadService.get_threads(
            db=db,
            user_id=current_user.id,
            category_id=params.category_id,
            is_archived=params.is_archived,
            is_pinned=params.is_pinned,
            search=params.search,
            skip=params.skip,
            limit=params.limit
        )

        # Формируем ответ
        result = []
        for thread in threads:
            # Получаем количество сообщений для треда
            message_count = await ThreadService.get_message_count(db, thread.id)

            # Получаем категорию, если она есть
            category = None
            if thread.category_id:
                category = await ThreadService.get_category_by_id(db, thread.category_id)

            # Создаем объект для ответа
            thread_dict = {
                "id": thread.id,
                "user_id": thread.user_id,
                "title": thread.title,
                "provider_id": thread.provider_id,
                "model_id": thread.model_id,
                "provider_code": thread.provider_code,
                "model_code": thread.model_code,
                "category_id": thread.category_id,
                "max_tokens": thread.max_tokens,
                "temperature": thread.temperature,
                "is_pinned": thread.is_pinned,
                "is_archived": thread.is_archived,
                "created_at": thread.created_at,
                "updated_at": thread.updated_at,
                "last_message_at": thread.last_message_at,
                "message_count": message_count,
                "category": category.__dict__ if category else None
            }

            result.append(ThreadSummarySchema(**thread_dict))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка тредов: {str(e)}"
        )


@router.get("/{thread_id}", response_model=ThreadSchema)
async def get_thread(
        thread_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает тред с указанным ID и всеми его сообщениями.
    """
    try:
        # Получаем тред и его сообщения
        thread, messages = await ThreadService.get_thread_with_messages(
            db=db,
            user_id=current_user.id,
            thread_id=thread_id
        )

        # Получаем категорию, если она есть
        category = None
        if thread.category_id:
            category = await ThreadService.get_category_by_id(db, thread.category_id)

        # Создаем объект для ответа
        thread_dict = {
            "id": thread.id,
            "user_id": thread.user_id,
            "title": thread.title,
            "provider_id": thread.provider_id,
            "model_id": thread.model_id,
            "provider_code": thread.provider_code,
            "model_code": thread.model_code,
            "category_id": thread.category_id,
            "is_pinned": thread.is_pinned,
            "is_archived": thread.is_archived,
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
            "last_message_at": thread.last_message_at,
            "message_count": len(messages),
            "max_tokens": thread.max_tokens,  # Добавлено поле max_tokens
            "temperature": thread.temperature,  # Добавлено поле temperature
            "category": category.__dict__ if category else None,
            "messages": []
        }

        # Добавляем сообщения
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "thread_id": msg.thread_id,
                "role": msg.role,
                "content": msg.content,
                "tokens_input": msg.tokens_input,
                "tokens_output": msg.tokens_output,
                "tokens_total": msg.tokens_total,
                "model_id": msg.model_id,
                "provider_id": msg.provider_id,
                "model_code": msg.model_code,
                "provider_code": msg.provider_code,
                "meta_data": msg.meta_data if msg.meta_data else {},
                "created_at": msg.created_at
            }
            thread_dict["messages"].append(msg_dict)

        return ThreadSchema(**thread_dict)

    except ThreadNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении треда: {str(e)}"
        )


@router.put("/{thread_id}", response_model=ThreadSchema)
async def update_thread(
        thread_id: int,
        thread_data: ThreadUpdateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Обновляет информацию о треде.
    """
    try:
        # Обновляем тред
        thread = await ThreadService.update_thread(
            db=db,
            user_id=current_user.id,
            thread_id=thread_id,
            thread_data=thread_data
        )

        # Получаем сообщения треда
        messages = await MessageService.get_messages_for_thread(db, thread_id)

        # Получаем категорию, если она есть
        category = None
        if thread.category_id:
            category = await ThreadService.get_category_by_id(db, thread.category_id)

        # Создаем объект для ответа
        thread_dict = {
            "id": thread.id,
            "user_id": thread.user_id,
            "title": thread.title,
            "provider_id": thread.provider_id,
            "model_id": thread.model_id,
            "provider_code": thread.provider_code,
            "model_code": thread.model_code,
            "category_id": thread.category_id,
            "is_pinned": thread.is_pinned,
            "is_archived": thread.is_archived,
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
            "last_message_at": thread.last_message_at,
            "message_count": len(messages),
            "category": category.__dict__ if category else None,
            "messages": []
        }

        # Добавляем сообщения
        for msg in messages:
            msg_dict = {
                "id": msg.id,
                "thread_id": msg.thread_id,
                "role": msg.role,
                "content": msg.content,
                "tokens_input": msg.tokens_input,
                "tokens_output": msg.tokens_output,
                "tokens_total": msg.tokens_total,
                "model_id": msg.model_id,
                "provider_id": msg.provider_id,
                "model_code": msg.model_code,
                "provider_code": msg.provider_code,
                "meta_data": msg.meta_data if msg.meta_data else {},
                "created_at": msg.created_at
            }
            thread_dict["messages"].append(msg_dict)

        return ThreadSchema(**thread_dict)

    except ThreadNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CategoryNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении треда: {str(e)}"
        )


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
        thread_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет тред с указанным ID.
    """
    try:
        await ThreadService.delete_thread(
            db=db,
            user_id=current_user.id,
            thread_id=thread_id
        )
        return None

    except ThreadNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении треда: {str(e)}"
        )


@router.post("/bulk-delete", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_threads(
        data: BulkThreadActionSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Массовое удаление тредов.
    """
    try:
        await ThreadService.bulk_delete_threads(
            db=db,
            user_id=current_user.id,
            thread_ids=data.thread_ids
        )
        return None

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при массовом удалении тредов: {str(e)}"
        )


@router.post("/bulk-archive", response_model=List[ThreadSummarySchema])
async def bulk_archive_threads(
        data: BulkThreadActionSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Массовое архивирование тредов.
    """
    try:
        # Архивируем треды
        threads = await ThreadService.bulk_archive_threads(
            db=db,
            user_id=current_user.id,
            thread_ids=data.thread_ids
        )

        # Формируем ответ
        result = []
        for thread in threads:
            # Получаем количество сообщений для треда
            message_count = await ThreadService.get_message_count(db, thread.id)

            # Получаем категорию, если она есть
            category = None
            if thread.category_id:
                category = await ThreadService.get_category_by_id(db, thread.category_id)

            # Создаем объект для ответа
            thread_dict = {
                "id": thread.id,
                "user_id": thread.user_id,
                "title": thread.title,
                "provider_id": thread.provider_id,
                "model_id": thread.model_id,
                "provider_code": thread.provider_code,
                "model_code": thread.model_code,
                "category_id": thread.category_id,
                "is_pinned": thread.is_pinned,
                "is_archived": thread.is_archived,
                "created_at": thread.created_at,
                "updated_at": thread.updated_at,
                "last_message_at": thread.last_message_at,
                "message_count": message_count,
                "category": category.__dict__ if category else None
            }

            result.append(ThreadSummarySchema(**thread_dict))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при массовом архивировании тредов: {str(e)}"
        )


@router.post("/{thread_id}/messages", response_model=MessageSchema)
async def add_message(
        thread_id: int,
        message: MessageCreateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Добавляет новое сообщение в тред.
    """
    try:
        # Проверяем доступ к треду
        await ThreadService.get_thread_by_id(db, current_user.id, thread_id)

        # Создаем новое сообщение
        if message.role == "user":
            new_message = await MessageService.create_user_message(
                db=db,
                thread_id=thread_id,
                content=message.content
            )
        elif message.role == "system":
            new_message = await MessageService.add_or_update_system_prompt(
                db=db,
                thread_id=thread_id,
                system_prompt=message.content
            )
        else:
            # Для других типов сообщений (например, assistant) используем прямое создание
            # Это может понадобиться для импорта истории из других чатов
            await ThreadService.get_thread_by_id(db, current_user.id, thread_id)

            new_message = MessageOrm(
                thread_id=thread_id,
                role=message.role,
                content=message.content,
                tokens_input=message.tokens_input,
                tokens_output=message.tokens_output,
                tokens_total=message.tokens_total,
                model_id=message.model_id,
                provider_id=message.provider_id,
                model_code=message.model_code,
                provider_code=message.provider_code,
                cost=message.cost,
                is_cached=message.is_cached,
                meta_data=message.metadata or {}
            )

            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)

            # Обновляем время последнего сообщения в треде
            await ThreadService.update_thread_activity(db, thread_id)

        return MessageSchema.from_orm(new_message)

    except ThreadNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении сообщения: {str(e)}"
        )


@router.post("/{thread_id}/send", response_model=MessageSchema)
async def send_message(
        thread_id: int,
        message_data: SendMessageRequestSchema,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user),
        use_context: bool = Query(True, description="Использовать контекст для генерации ответа")
):
    """
    Отправляет сообщение пользователя в тред и получает ответ от ИИ.

    Параметр use_context определяет, нужно ли использовать историю сообщений
    для формирования контекста диалога. Если False, будет отправлен только
    последний запрос пользователя.
    """
    try:
        result = await MessageService.send_message(
            db=db,
            user_id=current_user.id,
            thread_id=thread_id,
            message_data=message_data,
            background_tasks=background_tasks,
            use_context=use_context
        )

        # Проверяем, получили ли мы ошибку или сообщение
        if isinstance(result, dict) and result.get("error", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )

        return MessageSchema.from_orm(result)

    except ThreadNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except MessageServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке сообщения: {str(e)}"
        )


@router.post(
    "/completion",
    response_model=CompletionResponseSchema,
    responses={400: {"model": ErrorResponseSchema}, 500: {"model": ErrorResponseSchema}}
)
async def generate_completion(
        request: CompletionRequestSchema,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Генерирует ответ на основе запроса пользователя без сохранения в тред.
    """
    try:
        # Преобразуем запрос в словарь для передачи в сервис
        request_data = {
            "provider_id": request.provider_id,
            "model_preference_id": request.model_preference_id,  # Используем model_preference_id
            "prompt": request.prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "system_prompt": request.system_prompt
        }

        # Генерируем ответ через MessageService
        result = await MessageService.generate_completion_for_api(
            db=db,
            user_id=current_user.id,
            request_data=request_data,
            background_tasks=background_tasks
        )

        # Проверяем наличие ошибки
        if result.get("error", False):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if result.get(
                    "error_type") != "api_key_not_found" else status.HTTP_400_BAD_REQUEST,
                detail=result
            )

        return result

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации ответа: {str(e)}"
        )


@router.post(
    "/token-count",
    response_model=TokenCountResponseSchema
)
async def count_tokens(
        request: TokenCountRequestSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Подсчитывает количество токенов в тексте.
    Поддерживает запрос через model_preferences_id или через provider_id + model_id
    """
    try:
        # Если используется model_preferences_id, получаем provider_id и model_id из предпочтений
        if request.model_preferences_id:
            preference_query = select(ModelPreferencesOrm).filter(
                (ModelPreferencesOrm.id == request.model_preferences_id) &
                (ModelPreferencesOrm.user_id == current_user.id)
            )
            preference_result = await db.execute(preference_query)
            preference = preference_result.scalars().first()

            if not preference:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Предпочтение модели с ID {request.model_preferences_id} не найдено или принадлежит другому пользователю"
                )

            provider_id = preference.provider_id
            model_id = preference.model_id
        else:
            # Используем переданные provider_id и model_id
            provider_id = request.provider_id
            model_id = request.model_id

        # Вызываем существующий метод с полученными provider_id и model_id
        result = await MessageService.count_tokens(
            db=db,
            user_id=current_user.id,
            provider_id=provider_id,
            model_id=model_id,
            text=request.text
        )

        # Проверяем наличие ошибки
        if result.get("error", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при подсчете токенов: {str(e)}"
        )


@router.post("/{thread_id}/stream", response_class=StreamingResponse)
async def stream_message(
        thread_id: int,
        message_data: SendMessageRequestSchema,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user),
        use_context: bool = Query(True, description="Использовать контекст для генерации ответа"),
        timeout: int = Query(120, description="Таймаут генерации в секундах")
):
    try:
        # Проверяем доступ к треду
        await ThreadService.get_thread_by_id(db, current_user.id, thread_id)

        # Функция-генератор для потоковой передачи
        async def generate():
            try:
                # Используем MessageService для обработки потокового ответа
                async for chunk in MessageService.handle_stream_response(
                        db=db,
                        user_id=current_user.id,
                        thread_id=thread_id,
                        user_message_content=message_data.content,
                        background_tasks=background_tasks,
                        system_prompt=message_data.system_prompt,
                        max_tokens=message_data.max_tokens,
                        temperature=message_data.temperature,
                        use_context=use_context,
                        timeout=timeout,
                        connection_check_callback=None  # Передаем None вместо функции
                ):
                    # Отправляем чанк клиенту
                    yield f"data: {json.dumps(chunk)}\n\n"

            except Exception as e:
                # Обработка ошибок
                error_message = f"Ошибка при генерации потокового ответа: {str(e)}"
                yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

                # Сохраняем сообщение об ошибке в БД
                thread_result = await db.execute(
                    select(ThreadOrm).filter(ThreadOrm.id == thread_id)
                )
                thread = thread_result.scalar_one_or_none()

                if thread:
                    await MessageService.save_error_message(
                        db=db,
                        thread_id=thread_id,
                        error_message=error_message,
                        error_type="stream_error",
                        provider_id=thread.provider_id,
                        model_id=thread.model_id,
                        error_details=str(e)
                    )

        # Возвращаем стрим-ответ с правильными заголовками
        headers = {
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream'
        }
        return StreamingResponse(generate(), headers=headers)

    except ThreadNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при инициализации потока: {str(e)}"
        )


@router.post("/{thread_id}/stream/stop", status_code=status.HTTP_200_OK)
async def stop_streaming(
        thread_id: int,
        message_id: Optional[int] = None,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Прерывает генерацию ответа и сохраняет текущий результат.

    Args:
        thread_id: ID треда
        message_id: ID сообщения, если уже сохранено (опционально)
    """
    try:
        # Проверяем доступ к треду
        await ThreadService.get_thread_by_id(db, current_user.id, thread_id)

        # Если предоставлен ID сообщения, отмечаем его как прерванное
        if message_id:
            message_result = await db.execute(
                select(MessageOrm).filter(
                    (MessageOrm.id == message_id) &
                    (MessageOrm.thread_id == thread_id)
                )
            )
            message = message_result.scalar_one_or_none()

            if message:
                # Добавляем в метаданные информацию о прерывании
                if not message.meta_data:
                    message.meta_data = {}
                message.meta_data["stopped_early"] = True

                await db.commit()

        return {"success": True, "message": "Генерация прервана"}

    except ThreadNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при остановке потока: {str(e)}"
        )

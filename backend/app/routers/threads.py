import json
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi.responses import StreamingResponse
import asyncio

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, ThreadOrm, MessageOrm, ThreadCategoryOrm
from app.schemas.thread import (
    ThreadCreateSchema, ThreadUpdateSchema, ThreadSchema,
    ThreadSummarySchema, ThreadListParamsSchema, BulkThreadActionSchema,
    MessageCreateSchema, MessageSchema, SendMessageRequestSchema,
    CompletionRequestSchema, CompletionResponseSchema, TokenCountRequestSchema,
    TokenCountResponseSchema, ErrorResponseSchema
)
from app.services.ai_service_factory import AIServiceFactory
from app.services.message_service import process_and_save_message, get_or_create_model_preference

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
    # Проверяем категорию, если указана
    if thread_data.category_id:
        result = await db.execute(
            select(ThreadCategoryOrm).filter(
                (ThreadCategoryOrm.id == thread_data.category_id) &
                (ThreadCategoryOrm.user_id == current_user.id)
            )
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )

    # Создаем новый тред
    new_thread = ThreadOrm(
        user_id=current_user.id,
        title=thread_data.title,
        provider=thread_data.provider,
        model=thread_data.model,
        category_id=thread_data.category_id,
        is_pinned=thread_data.is_pinned,
        is_archived=thread_data.is_archived
    )

    db.add(new_thread)
    await db.commit()
    await db.refresh(new_thread)

    # Если предоставлено первое сообщение, добавляем его
    messages = []
    if thread_data.initial_message:
        # Добавляем системное сообщение, если указано
        if thread_data.system_prompt:
            system_message = MessageOrm(
                thread_id=new_thread.id,
                role="system",
                content=thread_data.system_prompt
            )
            db.add(system_message)
            messages.append(system_message)

        # Добавляем сообщение пользователя
        user_message = MessageOrm(
            thread_id=new_thread.id,
            role="user",
            content=thread_data.initial_message
        )
        db.add(user_message)
        messages.append(user_message)

        await db.commit()
        for msg in messages:
            await db.refresh(msg)

    # Получаем категорию, если она есть
    category_dict = None
    if new_thread.category_id:
        category_result = await db.execute(
            select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == new_thread.category_id)
        )
        category_orm = category_result.scalar_one_or_none()
        if category_orm:
            category_dict = {
                "id": category_orm.id,
                "user_id": category_orm.user_id,
                "name": category_orm.name,
                "description": category_orm.description,
                "color": category_orm.color,
                "created_at": category_orm.created_at,
                "updated_at": category_orm.updated_at
            }

    # Создаем словарь с данными треда
    thread_dict = {
        "id": new_thread.id,
        "user_id": new_thread.user_id,
        "title": new_thread.title,
        "provider": new_thread.provider,
        "model": new_thread.model,
        "category_id": new_thread.category_id,
        "is_pinned": new_thread.is_pinned,
        "is_archived": new_thread.is_archived,
        "created_at": new_thread.created_at,
        "updated_at": new_thread.updated_at,
        "last_message_at": new_thread.last_message_at,
        "message_count": len(messages),
        "category": category_dict,
        "messages": []
    }

    # Добавляем сообщения
    for msg in messages:
        # Преобразуем каждое сообщение в словарь
        msg_dict = {
            "id": msg.id,
            "thread_id": msg.thread_id,
            "role": msg.role,
            "content": msg.content,
            "tokens": msg.tokens,
            "model": msg.model,
            "provider": msg.provider,
            "meta_data": msg.meta_data if msg.meta_data else {},
            "created_at": msg.created_at
        }
        thread_dict["messages"].append(msg_dict)

    # Создаем объект схемы из словаря
    result = ThreadSchema(**thread_dict)

    return result

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

    # Проверяем категорию, если указана
    if thread_data.category_id:
        result = await db.execute(
            select(ThreadCategoryOrm).filter(
                (ThreadCategoryOrm.id == thread_data.category_id) &
                (ThreadCategoryOrm.user_id == current_user.id)
            )
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )

    # Создаем новый тред
    new_thread = ThreadOrm(
        user_id=current_user.id,
        title=thread_data.title,
        provider=thread_data.provider,
        model=thread_data.model,
        category_id=thread_data.category_id,
        is_pinned=thread_data.is_pinned,
        is_archived=thread_data.is_archived
    )

    db.add(new_thread)
    await db.commit()
    await db.refresh(new_thread)

    # Добавляем сообщения
    messages = []

    # Добавляем системное сообщение, если указано
    if thread_data.system_prompt:
        system_message = MessageOrm(
            thread_id=new_thread.id,
            role="system",
            content=thread_data.system_prompt
        )
        db.add(system_message)
        messages.append(system_message)

    # Добавляем сообщение пользователя
    user_message = MessageOrm(
        thread_id=new_thread.id,
        role="user",
        content=thread_data.initial_message
    )
    db.add(user_message)
    messages.append(user_message)

    await db.commit()
    for msg in messages:
        await db.refresh(msg)

    # Создаем сервис AI для указанного провайдера
    ai_service = await AIServiceFactory.create_service_for_user(
        db, current_user.id, thread_data.provider
    )

    if not ai_service:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "error_message": f"API ключ для провайдера {thread_data.provider} не найден",
                "error_type": "api_key_not_found"
            }
        )

    # Переменные для сбора полного ответа
    full_response = ""
    tokens_info = {}
    cost = 0

    # Функция генератор для потоковой передачи
    async def generate():
        nonlocal full_response, tokens_info, cost

        try:
            # Отправляем информацию о созданном треде
            thread_info = {
                "thread_id": new_thread.id,
                "title": new_thread.title,
                "provider": new_thread.provider,
                "model": new_thread.model,
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

            # Формируем контекст
            context = []
            if thread_data.system_prompt:
                context.append({"role": "system", "content": thread_data.system_prompt})
            context.append({"role": "user", "content": thread_data.initial_message})

            # Определяем параметры для запроса
            max_tokens = getattr(thread_data, 'max_tokens', 1000)
            temperature = getattr(thread_data, 'temperature', 0.7)

            # Генерируем ответ в потоковом режиме
            if thread_data.provider == "openai":
                async for chunk in ai_service.stream_completion_with_context(
                        context=context,
                        model=thread_data.model,
                        max_tokens=max_tokens,
                        temperature=temperature
                ):
                    # Добавляем кусок к полному ответу
                    if "text" in chunk:
                        full_response += chunk["text"]
                        # Отправляем кусок клиенту
                        yield f"data: {json.dumps({'text': chunk['text']})}\n\n"

                    # Сохраняем информацию о токенах и стоимости, если она есть
                    if "tokens" in chunk:
                        tokens_info = chunk["tokens"]
                    if "cost" in chunk:
                        cost = chunk["cost"]
            else:
                # Для других провайдеров используем обычный стриминг
                async for chunk in ai_service.stream_completion(
                        prompt=thread_data.initial_message,
                        model=thread_data.model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system_prompt=thread_data.system_prompt
                ):
                    # Аналогичная обработка
                    if "text" in chunk:
                        full_response += chunk["text"]
                        yield f"data: {json.dumps({'text': chunk['text']})}\n\n"

                    if "tokens" in chunk:
                        tokens_info = chunk["tokens"]
                    if "cost" in chunk:
                        cost = chunk["cost"]

            # После завершения стриминга сохраняем сообщение в БД
            assistant_message = MessageOrm(
                thread_id=new_thread.id,
                role="assistant",
                content=full_response,
                tokens=tokens_info.get("total_tokens", 0),
                model=thread_data.model,
                provider=thread_data.provider,
                meta_data={
                    "tokens": tokens_info,
                    "cost": cost,
                    "with_context": True
                }
            )
            db.add(assistant_message)

            # Обновляем время последнего сообщения в треде
            new_thread.last_message_at = datetime.now()
            new_thread.updated_at = datetime.now()

            await db.commit()
            await db.refresh(assistant_message)

            # Обновляем статистику использования в фоновом режиме
            background_tasks.add_task(
                ai_service.update_usage_statistics,
                db=db,
                user_id=current_user.id,
                tokens_data=tokens_info,
                model=thread_data.model,
                cost=cost
            )

            # Отправляем финальное сообщение с ID сохраненного сообщения
            yield f"data: {json.dumps({'done': True, 'message_id': assistant_message.id})}\n\n"

        except Exception as e:
            # Обработка ошибок
            error_message = f"Ошибка при генерации ответа: {str(e)}"
            yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

            # Сохраняем сообщение об ошибке в БД
            error_msg = MessageOrm(
                thread_id=new_thread.id,
                role="assistant",
                content=error_message,
                meta_data={"error": True, "error_type": "api_error", "error_details": str(e)},
                provider=thread_data.provider,
                model=thread_data.model
            )
            db.add(error_msg)
            await db.commit()

    # Возвращаем стрим-ответ с правильными заголовками
    headers = {
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'text/event-stream'
    }
    return StreamingResponse(generate(), headers=headers)


@router.get("/", response_model=List[ThreadSummarySchema])
async def get_threads(
        params: ThreadListParamsSchema = Depends(),
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает список тредов пользователя с пагинацией и фильтрацией.
    """
    # Базовый запрос
    query = select(ThreadOrm).filter(ThreadOrm.user_id == current_user.id)

    # Применяем фильтры
    if params.category_id is not None:
        query = query.filter(ThreadOrm.category_id == params.category_id)

    if params.is_archived is not None:
        query = query.filter(ThreadOrm.is_archived == params.is_archived)

    if params.is_pinned is not None:
        query = query.filter(ThreadOrm.is_pinned == params.is_pinned)

    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(ThreadOrm.title.ilike(search_term))

    # Сортировка: сначала закрепленные, потом по дате последнего сообщения
    query = query.order_by(ThreadOrm.is_pinned.desc(), ThreadOrm.last_message_at.desc())

    # Пагинация
    query = query.offset(params.skip).limit(params.limit)

    result = await db.execute(query)
    threads = result.scalars().all()

    # Подсчет сообщений для каждого треда и создание ответа
    result = []
    for thread in threads:
        # Получаем количество сообщений
        message_count_result = await db.execute(
            select(func.count(MessageOrm.id)).filter(MessageOrm.thread_id == thread.id)
        )
        message_count = message_count_result.scalar()

        # Создаем словарь для ответа из ORM-модели
        thread_dict = {
            "id": thread.id,
            "user_id": thread.user_id,
            "title": thread.title,
            "provider": thread.provider,
            "model": thread.model,
            "category_id": thread.category_id,
            "is_pinned": thread.is_pinned,
            "is_archived": thread.is_archived,
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
            "last_message_at": thread.last_message_at,
            "message_count": message_count
        }

        # Добавляем категорию, если она есть
        if thread.category_id:
            category_result = await db.execute(
                select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == thread.category_id)
            )
            category = category_result.scalar_one_or_none()
            if category:
                thread_dict["category"] = {
                    "id": category.id,
                    "user_id": category.user_id,
                    "name": category.name,
                    "description": category.description,
                    "color": category.color,
                    "created_at": category.created_at,
                    "updated_at": category.updated_at
                }
        else:
            thread_dict["category"] = None

        # Создаем схему из словаря
        thread_summary = ThreadSummarySchema(**thread_dict)
        result.append(thread_summary)

    return result


@router.get("/{thread_id}", response_model=ThreadSchema)
async def get_thread(
        thread_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает тред с указанным ID и всеми его сообщениями.
    """
    result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id == thread_id) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    thread = result.scalar_one_or_none()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден"
        )

    # Получаем все сообщения треда, отсортированные по времени создания
    messages_result = await db.execute(
        select(MessageOrm)
        .filter(MessageOrm.thread_id == thread_id)
        .order_by(MessageOrm.created_at)
    )
    messages = messages_result.scalars().all()

    # Подсчитываем количество сообщений
    message_count = len(messages)

    # Получаем категорию, если она есть
    category = None
    if thread.category_id:
        category_result = await db.execute(
            select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == thread.category_id)
        )
        category_orm = category_result.scalar_one_or_none()
        if category_orm:
            category = {
                "id": category_orm.id,
                "user_id": category_orm.user_id,
                "name": category_orm.name,
                "description": category_orm.description,
                "color": category_orm.color,
                "created_at": category_orm.created_at,
                "updated_at": category_orm.updated_at
            }

    # Создаем словарь с данными треда
    thread_dict = {
        "id": thread.id,
        "user_id": thread.user_id,
        "title": thread.title,
        "provider": thread.provider,
        "model": thread.model,
        "category_id": thread.category_id,
        "is_pinned": thread.is_pinned,
        "is_archived": thread.is_archived,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at,
        "last_message_at": thread.last_message_at,
        "message_count": message_count,
        "category": category,
        "messages": []
    }

    # Добавляем сообщения
    for msg in messages:
        # Преобразуем каждое сообщение в словарь
        msg_dict = {
            "id": msg.id,
            "thread_id": msg.thread_id,
            "role": msg.role,
            "content": msg.content,
            "tokens": msg.tokens,
            "model": msg.model,
            "provider": msg.provider,
            "meta_data": msg.meta_data if msg.meta_data else {},
            "created_at": msg.created_at
        }
        thread_dict["messages"].append(msg_dict)

    # Создаем объект схемы из словаря
    result = ThreadSchema(**thread_dict)

    return result


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
    result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id == thread_id) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    thread = result.scalar_one_or_none()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден"
        )

    # Проверяем категорию, если указана
    if thread_data.category_id is not None:
        if thread_data.category_id > 0:
            category_result = await db.execute(
                select(ThreadCategoryOrm).filter(
                    (ThreadCategoryOrm.id == thread_data.category_id) &
                    (ThreadCategoryOrm.user_id == current_user.id)
                )
            )
            category = category_result.scalar_one_or_none()

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Категория не найдена"
                )
        thread.category_id = thread_data.category_id

    # Обновляем поля треда
    if thread_data.title is not None:
        thread.title = thread_data.title

    if thread_data.is_pinned is not None:
        thread.is_pinned = thread_data.is_pinned

    if thread_data.is_archived is not None:
        thread.is_archived = thread_data.is_archived

    thread.updated_at = datetime.now()

    await db.commit()
    await db.refresh(thread)

    # Получаем все сообщения треда
    messages_result = await db.execute(
        select(MessageOrm)
        .filter(MessageOrm.thread_id == thread_id)
        .order_by(MessageOrm.created_at)
    )
    messages = messages_result.scalars().all()

    # Получаем категорию, если она есть
    category = None
    if thread.category_id:
        category_result = await db.execute(
            select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == thread.category_id)
        )
        category_orm = category_result.scalar_one_or_none()
        if category_orm:
            category = {
                "id": category_orm.id,
                "user_id": category_orm.user_id,
                "name": category_orm.name,
                "description": category_orm.description,
                "color": category_orm.color,
                "created_at": category_orm.created_at,
                "updated_at": category_orm.updated_at
            }

    # Создаем словарь с данными треда
    thread_dict = {
        "id": thread.id,
        "user_id": thread.user_id,
        "title": thread.title,
        "provider": thread.provider,
        "model": thread.model,
        "category_id": thread.category_id,
        "is_pinned": thread.is_pinned,
        "is_archived": thread.is_archived,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at,
        "last_message_at": thread.last_message_at,
        "message_count": len(messages),
        "category": category,
        "messages": []
    }

    # Добавляем сообщения
    for msg in messages:
        # Преобразуем каждое сообщение в словарь
        msg_dict = {
            "id": msg.id,
            "thread_id": msg.thread_id,
            "role": msg.role,
            "content": msg.content,
            "tokens": msg.tokens,
            "model": msg.model,
            "provider": msg.provider,
            "meta_data": msg.meta_data if msg.meta_data else {},
            "created_at": msg.created_at
        }
        thread_dict["messages"].append(msg_dict)

    # Создаем объект схемы из словаря
    result = ThreadSchema(**thread_dict)

    return result

@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
        thread_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет тред с указанным ID.
    """
    result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id == thread_id) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    thread = result.scalar_one_or_none()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден"
        )

    await db.delete(thread)
    await db.commit()

    return None


@router.post("/bulk-delete", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_threads(
        data: BulkThreadActionSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Массовое удаление тредов.
    """
    if not data.thread_ids:
        return None

    # Удаляем треды, принадлежащие пользователю
    await db.execute(
        delete(ThreadOrm).where(
            (ThreadOrm.id.in_(data.thread_ids)) &
            (ThreadOrm.user_id == current_user.id)
        )
    )

    await db.commit()

    return None


@router.post("/bulk-archive", response_model=List[ThreadSummarySchema])
async def bulk_archive_threads(
        data: BulkThreadActionSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Массовое архивирование тредов.
    """
    if not data.thread_ids:
        return []

    # Получаем треды пользователя из указанного списка
    result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id.in_(data.thread_ids)) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    threads = result.scalars().all()

    # Архивируем треды
    for thread in threads:
        thread.is_archived = True
        thread.updated_at = datetime.now()

    await db.commit()

    # Обновляем треды в ответе
    result = []
    for thread in threads:
        await db.refresh(thread)

        # Подсчет сообщений для треда
        message_count_result = await db.execute(
            select(func.count(MessageOrm.id)).filter(MessageOrm.thread_id == thread.id)
        )
        message_count = message_count_result.scalar()

        # Получаем категорию, если она есть
        category = None
        if thread.category_id:
            category_result = await db.execute(
                select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == thread.category_id)
            )
            category_orm = category_result.scalar_one_or_none()
            if category_orm:
                category = {
                    "id": category_orm.id,
                    "user_id": category_orm.user_id,
                    "name": category_orm.name,
                    "description": category_orm.description,
                    "color": category_orm.color,
                    "created_at": category_orm.created_at,
                    "updated_at": category_orm.updated_at
                }

        # Создаем словарь с данными треда
        thread_dict = {
            "id": thread.id,
            "user_id": thread.user_id,
            "title": thread.title,
            "provider": thread.provider,
            "model": thread.model,
            "category_id": thread.category_id,
            "is_pinned": thread.is_pinned,
            "is_archived": thread.is_archived,
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
            "last_message_at": thread.last_message_at,
            "message_count": message_count,
            "category": category
        }

        # Создаем объект схемы из словаря
        thread_summary = ThreadSummarySchema(**thread_dict)
        result.append(thread_summary)

    return result

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
    result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id == thread_id) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    thread = result.scalar_one_or_none()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден"
        )

    # Создаем новое сообщение
    new_message = MessageOrm(
        thread_id=thread_id,
        role=message.role,
        content=message.content,
        tokens=message.tokens,
        model=message.model,
        provider=message.provider,
        meta_data=message.metadata or {}
    )

    db.add(new_message)

    # Обновляем время последнего сообщения в треде
    thread.last_message_at = datetime.now()
    thread.updated_at = datetime.now()

    await db.commit()
    await db.refresh(new_message)

    return MessageSchema.from_orm(new_message)


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
    # Проверяем наличие треда
    thread_result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id == thread_id) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    thread = thread_result.scalar_one_or_none()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден"
        )

    print(f"Найден тред: {thread.id}, провайдер: {thread.provider}, модель: {thread.model}")

    # Создаем сервис AI для указанного провайдера
    ai_service = await AIServiceFactory.create_service_for_user(
        db, current_user.id, thread.provider
    )

    if not ai_service:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "error_message": f"API ключ для провайдера {thread.provider} не найден",
                "error_type": "api_key_not_found"
            }
        )

    print(f"Создан сервис AI для провайдера: {thread.provider}")

    # Сохраняем сообщение пользователя
    user_message = MessageOrm(
        thread_id=thread_id,
        role="user",
        content=message_data.content,
        tokens_input=0,  # будет заполнено позже, если доступно
        tokens_output=0,
        tokens_total=0,
        provider=thread.provider,
        model=thread.model
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    print(f"Сохранено сообщение пользователя с ID: {user_message.id}")

    # Находим или создаем настройки модели для расчета стоимости
    model_preference_id = await get_or_create_model_preference(
        db=db,
        user_id=current_user.id,
        provider=thread.provider,
        model=thread.model
    )

    # Определяем метод генерации в зависимости от параметра use_context
    result = None
    try:
        if use_context and thread.provider == "openai":  # Для OpenAI используем контекст
            # Получаем историю сообщений для контекста
            messages_result = await db.execute(
                select(MessageOrm)
                .filter(MessageOrm.thread_id == thread_id)
                .order_by(MessageOrm.created_at)
            )
            messages = messages_result.scalars().all()

            print(f"Получено {len(messages)} сообщений для контекста")

            # Формируем контекст для запроса к ИИ
            context = []
            for msg in messages:
                if msg.role == "system" and msg.content:
                    context.append({"role": "system", "content": msg.content})
                elif msg.role in ["user", "assistant"]:
                    context.append({"role": msg.role, "content": msg.content})

            # Если указан системный промпт в запросе, используем его
            if message_data.system_prompt:
                # Проверяем, есть ли уже системное сообщение
                has_system = any(msg.get("role") == "system" for msg in context)
                if has_system:
                    # Заменяем существующее системное сообщение
                    for i, msg in enumerate(context):
                        if msg.get("role") == "system":
                            context[i] = {"role": "system", "content": message_data.system_prompt}
                            break
                else:
                    # Добавляем новое системное сообщение в начало
                    context.insert(0, {"role": "system", "content": message_data.system_prompt})

            print(f"Отправляем запрос с контекстом из {len(context)} сообщений")

            # Генерируем ответ от ИИ с полным контекстом
            try:
                result = await ai_service.generate_completion_with_context(
                    context=context,
                    model=thread.model,
                    max_tokens=message_data.max_tokens,
                    temperature=message_data.temperature,
                    model_preference_id=model_preference_id
                )
                print(f"Получен ответ от OpenAI с контекстом")
            except Exception as e:
                print(f"Ошибка при вызове generate_completion_with_context: {str(e)}")
                # Пробуем использовать обычный generate_completion как резерв
                result = await ai_service.generate_completion(
                    prompt=message_data.content,
                    model=thread.model,
                    max_tokens=message_data.max_tokens,
                    temperature=message_data.temperature,
                    system_prompt=message_data.system_prompt,
                    model_preference_id=model_preference_id
                )
                print(f"Получен ответ через резервный метод")
        else:
            # Генерируем ответ от ИИ без контекста
            result = await ai_service.generate_completion(
                prompt=message_data.content,
                model=thread.model,
                max_tokens=message_data.max_tokens,
                temperature=message_data.temperature,
                system_prompt=message_data.system_prompt,
                model_preference_id=model_preference_id
            )
            print(f"Получен ответ от ИИ без контекста")

    except Exception as e:
        # Подробно логируем ошибку
        error_message = f"Ошибка при генерации ответа: {str(e)}, тип: {type(e).__name__}"
        print(error_message)

        # Создаем сообщение об ошибке
        error_msg = MessageOrm(
            thread_id=thread_id,
            role="assistant",
            content=error_message,
            meta_data={"error": True, "error_type": "api_error", "error_details": str(e)},
            provider=thread.provider,
            model=thread.model
        )
        db.add(error_msg)
        await db.commit()

        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "error_message": str(e),
                "error_type": "api_error"
            }
        )

    # Проверяем наличие ошибки в результате
    if result and result.get("error", False):
        error_msg = f"Ошибка API: {result.get('error_message', 'Неизвестная ошибка')}"
        print(error_msg)

        # Создаем сообщение об ошибке
        error_message = MessageOrm(
            thread_id=thread_id,
            role="assistant",
            content=error_msg,
            meta_data={"error": True, "error_type": result.get("error_type"), "error_details": result},
            provider=thread.provider,
            model=thread.model
        )
        db.add(error_message)
        await db.commit()
        await db.refresh(error_message)

        raise HTTPException(
            status_code=500,
            detail=result
        )

    print(f"Сохраняем ответ ассистента")

    # Обрабатываем и сохраняем ответ с использованием функции process_and_save_message
    try:
        assistant_message = await process_and_save_message(
            thread_id=thread_id,
            response_data=result,
            is_cached=False,
            model_preference_id=model_preference_id,
            db=db
        )
    except Exception as e:
        error_msg = f"Ошибка при обработке и сохранении ответа: {str(e)}"
        print(error_msg)

        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "error_message": error_msg,
                "error_type": "processing_error"
            }
        )

    # Обновляем время последнего сообщения в треде
    thread.last_message_at = datetime.now()
    thread.updated_at = datetime.now()

    try:
        await db.commit()
        print(f"Транзакция успешно завершена, сообщение сохранено с ID: {assistant_message.id}")
    except Exception as e:
        error_msg = f"Ошибка при обновлении треда: {str(e)}"
        print(error_msg)
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "error_message": error_msg,
                "error_type": "database_error"
            }
        )

    # Обновляем статистику использования в фоновом режиме
    try:
        background_tasks.add_task(
            ai_service.update_usage_statistics,
            db=db,
            user_id=current_user.id,
            tokens_data=result["tokens"],
            model=thread.model,
            cost=result["cost"]
        )
        print("Задача на обновление статистики добавлена")
    except Exception as e:
        print(f"Ошибка при добавлении фоновой задачи: {str(e)}")
        # Не возвращаем ошибку, так как статистика не критична для работы

    # Обновляем токены во входном сообщении пользователя, если они доступны
    if "tokens" in result and "prompt_tokens" in result["tokens"]:
        try:
            user_message.tokens_input = result["tokens"].get("prompt_tokens", 0)
            user_message.tokens_total = user_message.tokens_input
            await db.commit()
        except Exception as e:
            print(f"Ошибка при обновлении токенов сообщения пользователя: {str(e)}")
            # Не критичная ошибка, можно продолжать

    return MessageSchema.from_orm(assistant_message)

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
    # Создаем сервис AI для указанного провайдера
    ai_service = await AIServiceFactory.create_service_for_user(
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
    response_model=TokenCountResponseSchema
)
async def count_tokens(
        request: TokenCountRequestSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Подсчитывает количество токенов в тексте.
    """
    # Создаем сервис AI для указанного провайдера
    ai_service = await AIServiceFactory.create_service_for_user(
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

    # Подсчитываем токены
    result = await ai_service.calculate_tokens(
        text=request.text,
        model=request.model
    )

    return result


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
    """
    Отправляет сообщение пользователя в тред и получает потоковый ответ от ИИ.
    """
    # Проверяем наличие треда
    thread_result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id == thread_id) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    thread = thread_result.scalar_one_or_none()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден"
        )

    # Создаем сервис AI для указанного провайдера
    ai_service = await AIServiceFactory.create_service_for_user(
        db, current_user.id, thread.provider
    )

    if not ai_service:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "error_message": f"API ключ для провайдера {thread.provider} не найден",
                "error_type": "api_key_not_found"
            }
        )

    # Сохраняем сообщение пользователя
    user_message = MessageOrm(
        thread_id=thread_id,
        role="user",
        content=message_data.content,
        provider=thread.provider,
        model=thread.model
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # Переменные для сбора полного ответа
    full_response = ""
    tokens_info = {}
    cost = 0
    connection_alive = True

    # Функция-генератор для потоковой передачи
    async def generate():
        nonlocal full_response, tokens_info, cost, connection_alive

        # Проверка жизни соединения
        check_interval = 5  # секунд
        last_check = datetime.now()

        try:
            # Отправляем первое сообщение для подтверждения соединения
            yield f"data: {json.dumps({'status': 'connected', 'user_message_id': user_message.id})}\n\n"

            # Подготовка контекста, если нужно
            if use_context and thread.provider == "openai":
                # Получаем историю сообщений для контекста
                messages_result = await db.execute(
                    select(MessageOrm)
                    .filter(MessageOrm.thread_id == thread_id)
                    .order_by(MessageOrm.created_at)
                )
                messages = messages_result.scalars().all()

                # Формируем контекст для запроса к ИИ
                context = []
                for msg in messages:
                    if msg.role == "system" and msg.content:
                        context.append({"role": "system", "content": msg.content})
                    elif msg.role in ["user", "assistant"]:
                        context.append({"role": msg.role, "content": msg.content})

                # Если указан системный промпт в запросе, используем его
                if message_data.system_prompt:
                    has_system = any(msg.get("role") == "system" for msg in context)
                    if has_system:
                        for i, msg in enumerate(context):
                            if msg.get("role") == "system":
                                context[i] = {"role": "system", "content": message_data.system_prompt}
                                break
                    else:
                        context.insert(0, {"role": "system", "content": message_data.system_prompt})

                # Стрим с контекстом с таймаутом
                try:
                    async with asyncio.timeout(timeout):
                        async for chunk in ai_service.stream_completion_with_context(
                                context=context,
                                model=thread.model,
                                max_tokens=message_data.max_tokens,
                                temperature=message_data.temperature
                        ):
                            # Периодически проверяем живость соединения
                            now = datetime.now()
                            if (now - last_check).total_seconds() >= check_interval:
                                if not connection_alive:
                                    raise Exception("Client disconnected")
                                last_check = now

                            # Добавляем кусок к полному ответу
                            if "text" in chunk:
                                full_response += chunk["text"]
                                # Отправляем чанк клиенту
                                yield f"data: {json.dumps({'text': chunk['text']})}\n\n"

                            # Сохраняем информацию о токенах и стоимости, если она есть
                            if "tokens" in chunk:
                                tokens_info = chunk["tokens"]
                            if "cost" in chunk:
                                cost = chunk["cost"]
                except asyncio.TimeoutError:
                    raise Exception(f"Превышено время ожидания ({timeout} секунд)")
            else:
                # Стрим без контекста с таймаутом
                try:
                    async with asyncio.timeout(timeout):
                        async for chunk in ai_service.stream_completion(
                                prompt=message_data.content,
                                model=thread.model,
                                max_tokens=message_data.max_tokens,
                                temperature=message_data.temperature,
                                system_prompt=message_data.system_prompt
                        ):
                            # Периодическая проверка соединения
                            now = datetime.now()
                            if (now - last_check).total_seconds() >= check_interval:
                                if not connection_alive:
                                    raise Exception("Client disconnected")
                                last_check = now

                            # Добавляем кусок к полному ответу
                            if "text" in chunk:
                                full_response += chunk["text"]
                                # Отправляем чанк клиенту
                                yield f"data: {json.dumps({'text': chunk['text']})}\n\n"

                            # Сохраняем информацию о токенах и стоимости
                            if "tokens" in chunk:
                                tokens_info = chunk["tokens"]
                            if "cost" in chunk:
                                cost = chunk["cost"]
                except asyncio.TimeoutError:
                    raise Exception(f"Превышено время ожидания ({timeout} секунд)")

            # После завершения стриминга сохраняем сообщение в БД
            assistant_message = MessageOrm(
                thread_id=thread_id,
                role="assistant",
                content=full_response,
                tokens=tokens_info.get("total_tokens", 0),
                model=thread.model,
                provider=thread.provider,
                meta_data={
                    "tokens": tokens_info,
                    "cost": cost,
                    "with_context": use_context
                }
            )
            db.add(assistant_message)

            # Обновляем время последнего сообщения в треде
            thread.last_message_at = datetime.now()
            thread.updated_at = datetime.now()

            await db.commit()
            await db.refresh(assistant_message)

            # Обновляем статистику использования в фоновом режиме
            background_tasks.add_task(
                ai_service.update_usage_statistics,
                db=db,
                user_id=current_user.id,
                tokens_data=tokens_info,
                model=thread.model,
                cost=cost
            )

            # Отправляем финальное сообщение с ID сохраненного сообщения
            yield f"data: {json.dumps({'done': True, 'message_id': assistant_message.id})}\n\n"

        except Exception as e:
            # Обработка ошибок
            error_message = f"Ошибка при генерации ответа: {str(e)}"
            yield f"data: {json.dumps({'error': True, 'error_message': error_message})}\n\n"

            # Сохраняем сообщение об ошибке в БД
            error_msg = MessageOrm(
                thread_id=thread_id,
                role="assistant",
                content=error_message,
                meta_data={"error": True, "error_type": "api_error", "error_details": str(e)},
                provider=thread.provider,
                model=thread.model
            )
            db.add(error_msg)
            await db.commit()

    # Возвращаем стрим-ответ с правильными заголовками
    headers = {
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'text/event-stream'
    }
    response = StreamingResponse(generate(), headers=headers)

    # Добавляем обработчик закрытия соединения
    @response.background
    def on_disconnect():
        # Помечаем соединение как закрытое
        nonlocal connection_alive
        connection_alive = False

    return response


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
    # Проверяем доступ к треду
    result = await db.execute(
        select(ThreadOrm).filter(
            (ThreadOrm.id == thread_id) &
            (ThreadOrm.user_id == current_user.id)
        )
    )
    thread = result.scalar_one_or_none()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тред не найден"
        )

    # Отмечаем в БД, что сообщение было прервано (если ID предоставлен)
    if message_id:
        result = await db.execute(
            select(MessageOrm).filter(
                (MessageOrm.id == message_id) &
                (MessageOrm.thread_id == thread_id)
            )
        )
        message = result.scalar_one_or_none()

        if message:
            # Добавляем в метаданные информацию о прерывании
            if not message.meta_data:
                message.meta_data = {}
            message.meta_data["stopped_early"] = True

            await db.commit()

    return {"success": True, "message": "Генерация прервана"}

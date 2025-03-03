from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, SavedPromptOrm, ThreadCategoryOrm
from app.schemas.prompt import (
    SavedPromptSchema,
    SavedPromptCreateSchema,
    SavedPromptUpdateSchema,
    SavedPromptListParamsSchema
)

router = APIRouter()


@router.get("/", response_model=List[SavedPromptSchema])
async def get_prompts(
        params: SavedPromptListParamsSchema = Depends(),
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает список сохраненных промптов пользователя с фильтрацией.
    """
    # Базовый запрос
    query = select(SavedPromptOrm).filter(SavedPromptOrm.user_id == current_user.id)

    # Применяем фильтры
    if params.category_id is not None:
        query = query.filter(SavedPromptOrm.category_id == params.category_id)

    if params.is_favorite is not None:
        query = query.filter(SavedPromptOrm.is_favorite == params.is_favorite)

    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(
            or_(
                SavedPromptOrm.title.ilike(search_term),
                SavedPromptOrm.content.ilike(search_term),
                SavedPromptOrm.description.ilike(search_term)
            )
        )

    # Сортировка: сначала избранные, потом по дате обновления
    query = query.order_by(SavedPromptOrm.is_favorite.desc(), SavedPromptOrm.updated_at.desc())

    # Пагинация
    query = query.offset(params.skip).limit(params.limit)

    result = await db.execute(query)
    prompts = result.scalars().all()

    # Формируем результат в виде списка словарей
    result_prompts = []
    for prompt in prompts:
        # Создаем словарь с данными промпта
        prompt_dict = {
            "id": prompt.id,
            "user_id": prompt.user_id,
            "title": prompt.title,
            "content": prompt.content,
            "description": prompt.description,
            "category_id": prompt.category_id,
            "is_favorite": prompt.is_favorite,
            "created_at": prompt.created_at,
            "updated_at": prompt.updated_at,
            "category": None
        }

        # Добавляем категорию, если она есть
        if prompt.category_id:
            cat_result = await db.execute(
                select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == prompt.category_id)
            )
            category = cat_result.scalar_one_or_none()
            if category:
                prompt_dict["category"] = {
                    "id": category.id,
                    "name": category.name,
                    "color": category.color
                }

        # Создаем объект схемы из словаря
        prompt_schema = SavedPromptSchema(**prompt_dict)
        result_prompts.append(prompt_schema)

    return result_prompts


@router.get("/{prompt_id}", response_model=SavedPromptSchema)
async def get_prompt(
        prompt_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает сохраненный промпт по ID.
    """
    result = await db.execute(
        select(SavedPromptOrm).filter(
            (SavedPromptOrm.id == prompt_id) &
            (SavedPromptOrm.user_id == current_user.id)
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Промпт не найден"
        )

    # Создаем словарь с данными промпта
    prompt_dict = {
        "id": prompt.id,
        "user_id": prompt.user_id,
        "title": prompt.title,
        "content": prompt.content,
        "description": prompt.description,
        "category_id": prompt.category_id,
        "is_favorite": prompt.is_favorite,
        "created_at": prompt.created_at,
        "updated_at": prompt.updated_at,
        "category": None
    }

    # Добавляем информацию о категории, если она есть
    if prompt.category_id:
        cat_result = await db.execute(
            select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == prompt.category_id)
        )
        category = cat_result.scalar_one_or_none()
        if category:
            prompt_dict["category"] = {
                "id": category.id,
                "name": category.name,
                "color": category.color
            }

    # Создаем объект схемы из словаря
    prompt_schema = SavedPromptSchema(**prompt_dict)

    return prompt_schema


@router.post("/", response_model=SavedPromptSchema, status_code=status.HTTP_201_CREATED)
async def create_prompt(
        prompt_data: SavedPromptCreateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Создает новый сохраненный промпт.
    """
    # Проверяем категорию, если указана
    if prompt_data.category_id:
        result = await db.execute(
            select(ThreadCategoryOrm).filter(
                (ThreadCategoryOrm.id == prompt_data.category_id) &
                (ThreadCategoryOrm.user_id == current_user.id)
            )
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )

    # Создаем новый промпт
    new_prompt = SavedPromptOrm(
        user_id=current_user.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        category_id=prompt_data.category_id,
        is_favorite=prompt_data.is_favorite
    )

    db.add(new_prompt)
    await db.commit()
    await db.refresh(new_prompt)

    # Создаем словарь с данными промпта
    prompt_dict = {
        "id": new_prompt.id,
        "user_id": new_prompt.user_id,
        "title": new_prompt.title,
        "content": new_prompt.content,
        "description": new_prompt.description,
        "category_id": new_prompt.category_id,
        "is_favorite": new_prompt.is_favorite,
        "created_at": new_prompt.created_at,
        "updated_at": new_prompt.updated_at,
        "category": None
    }

    # Добавляем информацию о категории, если она есть
    if new_prompt.category_id:
        cat_result = await db.execute(
            select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == new_prompt.category_id)
        )
        category = cat_result.scalar_one_or_none()
        if category:
            prompt_dict["category"] = {
                "id": category.id,
                "name": category.name,
                "color": category.color
            }

    # Создаем объект схемы из словаря
    prompt_schema = SavedPromptSchema(**prompt_dict)

    return prompt_schema


@router.put("/{prompt_id}", response_model=SavedPromptSchema)
async def update_prompt(
        prompt_id: int,
        prompt_data: SavedPromptUpdateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Обновляет информацию о сохраненном промпте.
    """
    result = await db.execute(
        select(SavedPromptOrm).filter(
            (SavedPromptOrm.id == prompt_id) &
            (SavedPromptOrm.user_id == current_user.id)
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Промпт не найден"
        )

    # Проверяем категорию, если указана
    if prompt_data.category_id is not None:
        if prompt_data.category_id > 0:
            cat_result = await db.execute(
                select(ThreadCategoryOrm).filter(
                    (ThreadCategoryOrm.id == prompt_data.category_id) &
                    (ThreadCategoryOrm.user_id == current_user.id)
                )
            )
            category = cat_result.scalar_one_or_none()

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Категория не найдена"
                )
        prompt.category_id = prompt_data.category_id

    # Обновляем поля промпта
    if prompt_data.title is not None:
        prompt.title = prompt_data.title

    if prompt_data.content is not None:
        prompt.content = prompt_data.content

    if prompt_data.description is not None:
        prompt.description = prompt_data.description

    if prompt_data.is_favorite is not None:
        prompt.is_favorite = prompt_data.is_favorite

    await db.commit()
    await db.refresh(prompt)

    # Создаем словарь с данными промпта
    prompt_dict = {
        "id": prompt.id,
        "user_id": prompt.user_id,
        "title": prompt.title,
        "content": prompt.content,
        "description": prompt.description,
        "category_id": prompt.category_id,
        "is_favorite": prompt.is_favorite,
        "created_at": prompt.created_at,
        "updated_at": prompt.updated_at,
        "category": None
    }

    # Добавляем информацию о категории, если она есть
    if prompt.category_id:
        cat_result = await db.execute(
            select(ThreadCategoryOrm).filter(ThreadCategoryOrm.id == prompt.category_id)
        )
        category = cat_result.scalar_one_or_none()
        if category:
            prompt_dict["category"] = {
                "id": category.id,
                "name": category.name,
                "color": category.color
            }

    # Создаем объект схемы из словаря
    prompt_schema = SavedPromptSchema(**prompt_dict)

    return prompt_schema


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
        prompt_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет сохраненный промпт.
    """
    result = await db.execute(
        select(SavedPromptOrm).filter(
            (SavedPromptOrm.id == prompt_id) &
            (SavedPromptOrm.user_id == current_user.id)
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Промпт не найден"
        )

    await db.delete(prompt)
    await db.commit()

    return None
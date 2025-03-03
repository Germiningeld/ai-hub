from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, update

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, ThreadCategoryOrm, ThreadOrm
from app.schemas.thread import ThreadCategorySchema, ThreadCategoryCreateSchema, ThreadCategoryUpdateSchema

router = APIRouter()


@router.get("/", response_model=List[ThreadCategorySchema])
async def get_categories(
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Получает список всех категорий тредов пользователя.
    """
    result = await db.execute(
        select(ThreadCategoryOrm)
        .filter(ThreadCategoryOrm.user_id == current_user.id)
        .order_by(ThreadCategoryOrm.name)
    )
    categories = result.scalars().all()

    return categories


@router.post("/", response_model=ThreadCategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
        category_data: ThreadCategoryCreateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Создает новую категорию тредов.
    """
    # Проверяем, существует ли категория с таким именем
    result = await db.execute(
        select(ThreadCategoryOrm).filter(
            (ThreadCategoryOrm.user_id == current_user.id) &
            (ThreadCategoryOrm.name == category_data.name)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким именем уже существует"
        )

    # Создаем новую категорию
    new_category = ThreadCategoryOrm(
        user_id=current_user.id,
        name=category_data.name,
        description=category_data.description,
        color=category_data.color
    )

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category


@router.put("/{category_id}", response_model=ThreadCategorySchema)
async def update_category(
        category_id: int,
        category_data: ThreadCategoryUpdateSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Обновляет информацию о категории.
    """
    result = await db.execute(
        select(ThreadCategoryOrm).filter(
            (ThreadCategoryOrm.id == category_id) &
            (ThreadCategoryOrm.user_id == current_user.id)
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )

    # Проверяем, не существует ли категория с обновленным именем
    if category_data.name and category_data.name != category.name:
        result = await db.execute(
            select(ThreadCategoryOrm).filter(
                (ThreadCategoryOrm.user_id == current_user.id) &
                (ThreadCategoryOrm.name == category_data.name) &
                (ThreadCategoryOrm.id != category_id)
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким именем уже существует"
            )

    # Обновляем поля категории
    if category_data.name is not None:
        category.name = category_data.name

    if category_data.description is not None:
        category.description = category_data.description

    if category_data.color is not None:
        category.color = category_data.color

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Удаляет категорию. Треды из этой категории остаются, но их category_id устанавливается в NULL.
    """
    result = await db.execute(
        select(ThreadCategoryOrm).filter(
            (ThreadCategoryOrm.id == category_id) &
            (ThreadCategoryOrm.user_id == current_user.id)
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )

    # Удаляем связь с тредами
    await db.execute(
        update(ThreadOrm)
        .where(
            (ThreadOrm.category_id == category_id) &
            (ThreadOrm.user_id == current_user.id)
        )
        .values(category_id=None)
    )

    # Удаляем категорию
    await db.delete(category)
    await db.commit()

    return None
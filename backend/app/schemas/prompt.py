from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class SavedPromptBaseSchema(BaseModel):
    title: str = Field(..., description="Название промпта")
    content: str = Field(..., description="Содержание промпта")
    description: Optional[str] = Field(None, description="Описание промпта")
    category_id: Optional[int] = Field(None, description="ID категории промпта")
    is_favorite: Optional[bool] = Field(False, description="Добавлен ли промпт в избранное")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "План маркетингового исследования",
                "content": "Проанализируй целевую аудиторию продукта {название_продукта} и предложи стратегию продвижения в социальных сетях.",
                "description": "Промпт для создания маркетингового плана по продвижению продукта",
                "category_id": 3,
                "is_favorite": True
            }
        }

class SavedPromptCreateSchema(SavedPromptBaseSchema):
    pass

class SavedPromptUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, description="Название промпта")
    content: Optional[str] = Field(None, description="Содержание промпта")
    description: Optional[str] = Field(None, description="Описание промпта")
    category_id: Optional[int] = Field(None, description="ID категории промпта")
    is_favorite: Optional[bool] = Field(None, description="Добавлен ли промпт в избранное")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Улучшенный план исследования",
                "content": "Разработай детальный план исследования по теме {тема_исследования}, включающий методологию, ключевые вопросы и ожидаемые результаты.",
                "description": "Обновленная версия промпта для научных исследований",
                "category_id": 2,
                "is_favorite": True
            }
        }

class SavedPromptSchema(SavedPromptBaseSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[dict] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 42,
                "user_id": 123,
                "title": "Генерация идей для статьи",
                "content": "Предложи 5 креативных идей для статьи на тему {тема}",
                "description": "Промпт для быстрой генерации идей для контент-плана",
                "category_id": 5,
                "is_favorite": False,
                "created_at": "2025-02-15T14:30:45",
                "updated_at": "2025-02-16T09:12:33",
                "category": {
                    "id": 5,
                    "name": "Контент-маркетинг",
                    "description": "Промпты для создания контента"
                }
            }
        }

class SavedPromptListParamsSchema(BaseModel):
    skip: Optional[int] = Field(0, description="Пропустить указанное количество промптов")
    limit: Optional[int] = Field(100, description="Максимальное количество возвращаемых промптов")
    category_id: Optional[int] = Field(None, description="Фильтр по ID категории")
    is_favorite: Optional[bool] = Field(None, description="Фильтр по избранным промптам")
    search: Optional[str] = Field(None, description="Текст для поиска в названиях и содержании промптов")

    class Config:
        json_schema_extra = {
            "example": {
                "skip": 10,
                "limit": 20,
                "category_id": 3,
                "is_favorite": True,
                "search": "маркетинг"
            }
        }
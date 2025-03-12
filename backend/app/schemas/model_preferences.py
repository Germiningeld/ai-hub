from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class AvailableModelSchema(BaseModel):
    """Схема для доступной модели от провайдера"""
    id: Optional[int] = Field(None, description="Идентификатор настроек модели")
    model: str = Field(..., description="Идентификатор модели (например, gpt-4o, claude-3-opus)")
    provider: str = Field(..., description="Провайдер модели (openai, anthropic, etc.)")
    max_tokens: Optional[int] = Field(None, description="Максимальное количество токенов")
    input_cost: Optional[float] = Field(None, description="Стоимость входных токенов за 1K")
    output_cost: Optional[float] = Field(None, description="Стоимость выходных токенов за 1K")
    cached_input_cost: Optional[float] = Field(None, description="Стоимость кэшированных входных токенов за 1K")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 42,
                "model": "gpt-4o",
                "provider": "openai",
                "max_tokens": 4096,
                "input_cost": 10.0,
                "output_cost": 30.0,
                "cached_input_cost": 3.0
            }
        }


class AvailableModelsResponseSchema(BaseModel):
    """Схема ответа со списком доступных моделей"""
    models: List[AvailableModelSchema] = Field(..., description="Список доступных моделей")

    class Config:
        json_schema_extra = {
            "example": {
                "models": [
                    {
                        "model": "gpt-4o",
                        "provider": "openai",
                        "max_tokens": 4096,
                        "input_cost": 10.0,
                        "output_cost": 30.0,
                        "cached_input_cost": 3.0
                    },
                    {
                        "model": "claude-3-opus",
                        "provider": "anthropic",
                        "max_tokens": 4096,
                        "input_cost": 15.0,
                        "output_cost": 75.0,
                        "cached_input_cost": 4.5
                    }
                ]
            }
        }


class ModelPreferencesBaseSchema(BaseModel):
    """Базовая схема для настроек модели"""
    provider: str = Field(..., description="Провайдер модели (openai, anthropic, etc.)")
    model: str = Field(..., description="Название модели (gpt-4o, claude-3-opus, etc.)")
    description: Optional[str] = Field(None, description="Описание настроек модели")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")
    system_prompt: Optional[str] = Field(None, description="Системный промпт по умолчанию")
    is_default: Optional[bool] = Field(False, description="Установить как модель по умолчанию для провайдера")
    input_cost: Optional[float] = Field(None, description="Стоимость входных токенов за 1K")
    output_cost: Optional[float] = Field(None, description="Стоимость выходных токенов за 1K")
    cached_input_cost: Optional[float] = Field(None, description="Стоимость кэшированных входных токенов за 1K")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4o",
                "description": "Настройки для аналитических задач",
                "max_tokens": 2000,
                "temperature": 0.8,
                "system_prompt": "Ты опытный помощник, который дает точные и полезные ответы",
                "is_default": True,
                "input_cost": 10.0,
                "output_cost": 30.0,
                "cached_input_cost": 3.0
            }
        }


class ModelPreferencesCreateSchema(ModelPreferencesBaseSchema):
    """Схема для создания настроек модели"""
    api_key_id: int = Field(..., description="ID API-ключа")


class ModelPreferencesUpdateSchema(BaseModel):
    """Схема для обновления настроек модели"""
    api_key_id: Optional[int] = Field(None, description="ID API-ключа")
    description: Optional[str] = Field(None, description="Описание настроек модели")
    max_tokens: Optional[int] = Field(None, description="Максимальное количество токенов")
    temperature: Optional[float] = Field(None, description="Температура (случайность) ответа")
    system_prompt: Optional[str] = Field(None, description="Системный промпт по умолчанию")
    is_default: Optional[bool] = Field(None, description="Установить как модель по умолчанию для провайдера")
    input_cost: Optional[float] = Field(None, description="Стоимость входных токенов за 1K")
    output_cost: Optional[float] = Field(None, description="Стоимость выходных токенов за 1K")
    cached_input_cost: Optional[float] = Field(None, description="Стоимость кэшированных входных токенов за 1K")

    class Config:
        json_schema_extra = {
            "example": {
                "api_key_id": 5,
                "max_tokens": 1500,
                "temperature": 0.5,
                "system_prompt": "Ты эксперт по Python и задачам машинного обучения",
                "is_default": True,
                "input_cost": 10.0,
                "output_cost": 30.0,
                "cached_input_cost": 3.0
            }
        }


class ModelPreferencesSchema(ModelPreferencesBaseSchema):
    """Полная схема настроек модели"""
    id: int
    user_id: int
    api_key_id: int  # Добавляем api_key_id
    created_at: datetime
    updated_at: datetime
    use_count: int = Field(0, description="Количество использований настроек")
    last_used_at: Optional[datetime] = Field(None, description="Время последнего использования")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 42,
                "user_id": 156,
                "api_key_id": 23,
                "provider": "openai",
                "model": "gpt-4o",
                "description": "Настройки для аналитических задач",
                "max_tokens": 2000,
                "temperature": 0.8,
                "system_prompt": "Ты опытный помощник, который дает точные и полезные ответы",
                "is_default": True,
                "input_cost": 10.0,
                "output_cost": 30.0,
                "cached_input_cost": 3.0,
                "created_at": "2024-02-10T09:15:32.123456",
                "updated_at": "2024-03-15T18:45:10.987654",
                "use_count": 15,
                "last_used_at": "2024-03-16T10:30:45.123456"
            }
        }
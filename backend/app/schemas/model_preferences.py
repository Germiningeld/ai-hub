from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class ModelPreferencesBaseSchema(BaseModel):
    provider: str = Field(..., description="Провайдер ИИ (openai, anthropic)")
    model: str = Field(..., description="Модель ИИ (gpt-4, claude-3-opus, и т.д.)")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")
    system_prompt: Optional[str] = Field(None, description="Системный промпт по умолчанию")
    is_default: Optional[bool] = Field(False, description="Является ли эта модель используемой по умолчанию")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "anthropic",
                "model": "claude-3-opus",
                "max_tokens": 2000,
                "temperature": 0.5,
                "system_prompt": "Ты профессиональный копирайтер, специализирующийся на создании рекламных текстов",
                "is_default": True
            }
        }

class ModelPreferencesCreateSchema(ModelPreferencesBaseSchema):
    pass

class ModelPreferencesUpdateSchema(BaseModel):
    max_tokens: Optional[int] = Field(None, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(None, description="Температура (случайность) ответа")
    system_prompt: Optional[str] = Field(None, description="Системный промпт по умолчанию")
    is_default: Optional[bool] = Field(None, description="Является ли эта модель используемой по умолчанию")

    class Config:
        json_schema_extra = {
            "example": {
                "max_tokens": 4000,
                "temperature": 0.3,
                "system_prompt": "Ты опытный научный консультант с глубокими знаниями в области медицины и биологии",
                "is_default": True
            }
        }

class ModelPreferencesSchema(ModelPreferencesBaseSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 15,
                "user_id": 324,
                "provider": "openai",
                "model": "gpt-4",
                "max_tokens": 1500,
                "temperature": 0.8,
                "system_prompt": "Ты аналитик данных, помогающий интерпретировать сложные наборы данных и строить прогнозы",
                "is_default": False,
                "created_at": "2025-02-10T12:30:45",
                "updated_at": "2025-02-15T18:22:33"
            }
        }

class AvailableModelSchema(BaseModel):
    provider: str = Field(..., description="Провайдер ИИ")
    id: str = Field(..., description="Идентификатор модели")
    name: str = Field(..., description="Название модели")
    description: Optional[str] = Field(None, description="Описание модели")
    max_tokens: int = Field(..., description="Максимальное количество токенов, поддерживаемое моделью")
    pricing: Dict[str, float] = Field(..., description="Цены за 1000 токенов (входные и выходные)")
    capabilities: List[str] = Field(..., description="Возможности модели")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "anthropic",
                "id": "claude-3-opus",
                "name": "Claude 3 Opus",
                "description": "Самая мощная модель Claude, оптимизированная для сложных задач рассуждения и творческой работы",
                "max_tokens": 200000,
                "pricing": {
                    "input": 15.0,
                    "output": 75.0
                },
                "capabilities": ["рассуждение", "креативное письмо", "программирование", "математика", "анализ данных"]
            }
        }

class AvailableModelsResponseSchema(BaseModel):
    models: List[AvailableModelSchema] = Field(..., description="Список доступных моделей")

    class Config:
        json_schema_extra = {
            "example": {
                "models": [
                    {
                        "provider": "openai",
                        "id": "gpt-4",
                        "name": "GPT-4",
                        "description": "Передовая модель OpenAI с высокой способностью к рассуждению",
                        "max_tokens": 8192,
                        "pricing": {
                            "input": 10.0,
                            "output": 30.0
                        },
                        "capabilities": ["рассуждение", "креативное письмо", "программирование"]
                    },
                    {
                        "provider": "anthropic",
                        "id": "claude-3-opus",
                        "name": "Claude 3 Opus",
                        "description": "Самая мощная модель Claude, оптимизированная для сложных задач",
                        "max_tokens": 200000,
                        "pricing": {
                            "input": 15.0,
                            "output": 75.0
                        },
                        "capabilities": ["рассуждение", "креативное письмо", "программирование", "математика", "анализ данных"]
                    }
                ]
            }
        }
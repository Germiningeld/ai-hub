from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    """Запрос на создание ответа от AI"""
    provider: str = Field(..., description="Провайдер AI (openai или anthropic)")
    model: str = Field(..., description="Модель (gpt-3.5-turbo, gpt-4, claude-3-opus и т.д.)")
    prompt: str = Field(..., description="Текст запроса")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")
    system_prompt: Optional[str] = Field(None, description="Системный промпт (инструкции для модели)")

    class Config:
        schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "prompt": "Расскажи о квантовой физике простыми словами",
                "max_tokens": 1000,
                "temperature": 0.7,
                "system_prompt": "Ты эксперт в науке, который умеет объяснять сложные концепции простым языком"
            }
        }


class CompletionResponse(BaseModel):
    """Ответ от AI"""
    text: str = Field(..., description="Текст ответа")
    model: str = Field(..., description="Использованная модель")
    provider: str = Field(..., description="Провайдер AI")
    tokens: Dict[str, int] = Field(..., description="Информация о токенах")
    cost: float = Field(..., description="Стоимость запроса в долларах")

    class Config:
        schema_extra = {
            "example": {
                "text": "Квантовая физика изучает поведение частиц на очень маленьких масштабах...",
                "model": "gpt-3.5-turbo",
                "provider": "openai",
                "tokens": {
                    "prompt_tokens": 25,
                    "completion_tokens": 150,
                    "total_tokens": 175
                },
                "cost": 0.00035
            }
        }


class TokenCountRequest(BaseModel):
    """Запрос на подсчет токенов в тексте"""
    provider: str = Field(..., description="Провайдер AI (openai или anthropic)")
    model: str = Field(..., description="Модель (gpt-3.5-turbo, gpt-4, claude-3-opus и т.д.)")
    text: str = Field(..., description="Текст для подсчета токенов")

    class Config:
        schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "text": "Расскажи о квантовой физике простыми словами"
            }
        }


class TokenCountResponse(BaseModel):
    """Ответ с количеством токенов"""
    token_count: int = Field(..., description="Количество токенов")
    estimated: Optional[bool] = Field(False, description="Флаг, указывающий, является ли подсчет оценочным")

    class Config:
        schema_extra = {
            "example": {
                "token_count": 7,
                "estimated": False
            }
        }


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    error: bool = Field(True, description="Флаг ошибки")
    error_message: str = Field(..., description="Текст ошибки")
    error_type: str = Field(..., description="Тип ошибки (routers, rate_limit, billing, etc.)")

    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "error_message": "Rate limit exceeded. Please try again later.",
                "error_type": "rate_limit"
            }
        }
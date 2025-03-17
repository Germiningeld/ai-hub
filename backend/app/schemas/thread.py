from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, constr
from enum import Enum


class RoleEnum(str, Enum):
    """Перечисление ролей в диалоге"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ProviderEnum(str, Enum):
    """Перечисление поддерживаемых провайдеров"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"


class ThreadCategoryCreateSchema(BaseModel):
    """Схема для создания новой категории тредов"""
    name: constr(min_length=1, max_length=100) = Field(..., description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")
    color: Optional[str] = Field(None, description="Цветовая метка категории в HEX формате")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Работа",
                "description": "Треды, связанные с рабочими задачами",
                "color": "#4A90E2"
            }
        }


class ThreadCategoryUpdateSchema(BaseModel):
    """Схема для обновления категории тредов"""
    name: Optional[constr(min_length=1, max_length=100)] = Field(None, description="Новое название категории")
    description: Optional[str] = Field(None, description="Новое описание категории")
    color: Optional[str] = Field(None, description="Новая цветовая метка категории в HEX формате")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Рабочие задачи",
                "description": "Треды, связанные с задачами на работе",
                "color": "#2E86C1"
            }
        }


class ThreadCategorySchema(BaseModel):
    """Схема категории треда"""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "name": "Работа",
                "description": "Треды, связанные с рабочими задачами",
                "color": "#4A90E2",
                "created_at": "2023-08-15T10:00:00",
                "updated_at": "2023-08-15T10:00:00"
            }
        }


class MessageSchema(BaseModel):
    """Схема сообщения"""
    id: int
    thread_id: int
    role: str
    content: str
    tokens_total: Optional[int] = 0
    tokens_input: Optional[int] = 0
    tokens_output: Optional[int] = 0
    provider_id: Optional[int] = None
    provider_code: Optional[str] = None
    model_id: Optional[int] = None
    model_code: Optional[str] = None
    cost: Optional[float] = 0.0
    is_cached: Optional[bool] = False
    model_preference_id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = {}
    created_at: datetime

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "thread_id": 1,
                "role": "user",
                "content": "Как мне реализовать сервис для работы с OpenAI API?",
                "tokens_total": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "provider_id": 1,
                "provider_code": "openai",
                "model_id": 1,
                "model_code": "gpt-3.5-turbo",
                "cost": 0.0,
                "is_cached": False,
                "meta_data": {},
                "created_at": "2023-08-15T10:05:00"
            }
        }


class MessageCreateSchema(BaseModel):
    """Схема для создания нового сообщения"""
    content: str = Field(..., description="Текст сообщения")
    role: Optional[str] = Field("user", description="Роль отправителя сообщения")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Как мне использовать OpenAI API в моем приложении?",
                "role": "user"
            }
        }


class ThreadSummarySchema(BaseModel):
    """Краткая схема треда"""
    id: int
    title: str
    provider_id: int
    provider_code: Optional[str] = None
    model_id: int
    model_code: Optional[str] = None
    category_id: Optional[int] = None
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int = 0
    max_tokens: Optional[int] = None  # Изменено с max_completion_tokens
    temperature: Optional[float] = None
    category: Optional[ThreadCategorySchema] = None

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Вопросы по OpenAI API",
                "provider_id": 1,
                "provider_code": "openai",
                "model_id": 1,
                "model_code": "gpt-3.5-turbo",
                "category_id": 1,
                "is_pinned": False,
                "is_archived": False,
                "created_at": "2023-08-15T10:00:00",
                "updated_at": "2023-08-15T10:05:00",
                "last_message_at": "2023-08-15T10:05:00",
                "message_count": 1,
                "category": {
                    "id": 1,
                    "name": "Работа",
                    "description": "Треды, связанные с рабочими задачами",
                    "color": "#4A90E2",
                    "created_at": "2023-08-15T10:00:00",
                    "updated_at": "2023-08-15T10:00:00"
                }
            }
        }

class ThreadSchema(ThreadSummarySchema):
    """Полная схема треда с сообщениями"""
    messages: List[MessageSchema] = []

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Вопросы по OpenAI API",
                "provider_id": 1,
                "provider_code": "openai",
                "model_id": 1,
                "model_code": "gpt-3.5-turbo",
                "category_id": 1,
                "is_pinned": False,
                "is_archived": False,
                "created_at": "2023-08-15T10:00:00",
                "updated_at": "2023-08-15T10:05:00",
                "last_message_at": "2023-08-15T10:05:00",
                "message_count": 2,
                "category": {
                    "id": 1,
                    "name": "Работа",
                    "description": "Треды, связанные с рабочими задачами",
                    "color": "#4A90E2",
                    "created_at": "2023-08-15T10:00:00",
                    "updated_at": "2023-08-15T10:00:00"
                },
                "messages": [
                    {
                        "id": 1,
                        "thread_id": 1,
                        "role": "user",
                        "content": "Как мне использовать OpenAI API в моем приложении?",
                        "tokens_total": 0,
                        "provider_id": 1,
                        "provider_code": "openai",
                        "model_id": 1,
                        "model_code": "gpt-3.5-turbo",
                        "meta_data": {},
                        "created_at": "2023-08-15T10:05:00"
                    },
                    {
                        "id": 2,
                        "thread_id": 1,
                        "role": "assistant",
                        "content": "Для использования OpenAI API вам нужно получить API ключ и установить библиотеку openai...",
                        "tokens_total": 150,
                        "tokens_input": 50,
                        "tokens_output": 100,
                        "provider_id": 1,
                        "provider_code": "openai",
                        "model_id": 1,
                        "model_code": "gpt-3.5-turbo",
                        "cost": 0.001,
                        "meta_data": {
                            "tokens": {
                                "prompt_tokens": 50,
                                "completion_tokens": 100,
                                "total_tokens": 150
                            }
                        },
                        "created_at": "2023-08-15T10:05:05"
                    }
                ]
            }
        }


class ThreadCreateSchema(BaseModel):
    """Схема для создания нового треда"""
    title: constr(min_length=1, max_length=255) = Field(..., description="Название треда")
    model_preferences_id: int = Field(..., description="ID предпочтения модели пользователя")
    category_id: Optional[int] = Field(None, description="ID категории треда")
    is_pinned: Optional[bool] = Field(False, description="Флаг закрепления треда")
    is_archived: Optional[bool] = Field(False, description="Флаг архивации треда")
    initial_message: Optional[str] = Field(None, description="Начальное сообщение пользователя")
    system_prompt: Optional[str] = Field(None, description="Системный промпт для модели (если указан, обновит системный промпт в предпочтениях)")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Вопросы по OpenAI API",
                "model_preferences_id": 7,
                "category_id": 1,
                "is_pinned": False,
                "is_archived": False,
                "initial_message": "Как мне использовать OpenAI API в моем приложении?",
                "system_prompt": "Ты - опытный инженер, специализирующийся на интеграции AI API."
            }
        }


class ThreadUpdateSchema(BaseModel):
    """Схема для обновления треда"""
    title: Optional[str] = Field(None, description="Название треда")
    category_id: Optional[int] = Field(None, description="ID категории треда")
    is_pinned: Optional[bool] = Field(None, description="Флаг закрепления треда")
    is_archived: Optional[bool] = Field(None, description="Флаг архивации треда")
    model_preference_id: Optional[int] = Field(None, description="ID предпочтения модели")
    max_tokens: Optional[int] = Field(None, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(None, description="Температура (случайность) ответа")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Интеграция с OpenAI API",
                "category_id": 2,
                "is_pinned": True,
                "is_archived": False,
                "model_preference_id": 14,
                "max_tokens": 1200,
                "temperature": 0.8
            }
        }


class ThreadListParamsSchema(BaseModel):
    """Параметры для получения списка тредов"""
    category_id: Optional[int] = Field(None, description="Фильтр по ID категории")
    is_archived: Optional[bool] = Field(None, description="Фильтр по статусу архивации")
    is_pinned: Optional[bool] = Field(None, description="Фильтр по статусу закрепления")
    search: Optional[str] = Field(None, description="Поисковый запрос")
    skip: int = Field(0, description="Количество пропускаемых записей для пагинации")
    limit: int = Field(100, description="Максимальное количество записей для возврата")

    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "is_archived": False,
                "is_pinned": None,
                "search": "OpenAI",
                "skip": 0,
                "limit": 20
            }
        }


class BulkThreadActionSchema(BaseModel):
    """Схема для массовых действий с тредами"""
    thread_ids: List[int] = Field(..., description="Список ID тредов")

    class Config:
        json_schema_extra = {
            "example": {
                "thread_ids": [1, 2, 3, 4, 5]
            }
        }


class SendMessageRequestSchema(BaseModel):
    """Схема для отправки сообщения в тред"""
    content: str = Field(..., description="Текст сообщения")
    system_prompt: Optional[str] = Field(None, description="Системный промпт для модели")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")

    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Температура должна быть в диапазоне от 0 до 1')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Какие есть библиотеки для работы с OpenAI API на Python?",
                "system_prompt": "Ты - опытный Python разработчик.",
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }


class CompletionRequestSchema(BaseModel):
    """Схема для запроса на генерацию текста без сохранения в тред"""
    prompt: str = Field(..., description="Текст запроса")
    provider_id: int = Field(..., description="ID провайдера AI")
    model_preference_id: int = Field(..., description="ID предпочтений модели")
    system_prompt: Optional[str] = Field(None, description="Системный промпт для модели")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")

    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Температура должна быть в диапазоне от 0 до 1')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Напиши простую функцию на Python для подсчета слов в тексте",
                "provider_id": 1,
                "model_preference_id": 7,
                "system_prompt": "Ты - опытный Python разработчик.",
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }


class CompletionResponseSchema(BaseModel):
    """Схема ответа на запрос генерации текста"""
    text: str = Field(..., description="Сгенерированный текст")
    model: Optional[str] = None
    provider: Optional[str] = None
    tokens: Dict[str, int] = Field(..., description="Информация о токенах")
    cost: Optional[float] = Field(None, description="Стоимость запроса")
    from_cache: Optional[bool] = False

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Вот простая функция для подсчета слов в тексте:\n\n```python\ndef count_words(text):\n    if not text:\n        return 0\n    words = text.split()\n    return len(words)\n```\n\nПример использования:\n\n```python\ntext = 'Привет, мир! Это пример текста.'\nword_count = count_words(text)\nprint(f'Количество слов: {word_count}')\n# Выведет: Количество слов: 5\n```",
                "model": "gpt-3.5-turbo",
                "provider": "openai",
                "tokens": {
                    "prompt_tokens": 50,
                    "completion_tokens": 120,
                    "total_tokens": 170
                },
                "cost": 0.0015,
                "from_cache": False
            }
        }


class TokenCountRequestSchema(BaseModel):
    """Схема запроса для подсчета токенов"""
    text: str = Field(..., description="Текст для подсчета токенов")
    provider_id: Optional[int] = Field(None, description="ID провайдера AI (необязательно при указании model_preferences_id)")
    model_id: Optional[int] = Field(None, description="ID модели AI (необязательно при указании model_preferences_id)")
    model_preferences_id: Optional[int] = Field(None, description="ID предпочтений модели (альтернатива указанию provider_id и model_id)")

    @validator('model_preferences_id')
    def validate_model_preferences_id(cls, v, values):
        """Проверяет, что либо указан model_preferences_id, либо provider_id и model_id"""
        provider_id = values.get('provider_id')
        model_id = values.get('model_id')
        if v is None and (provider_id is None or model_id is None):
            raise ValueError("Необходимо указать либо model_preferences_id, либо оба поля provider_id и model_id")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Напиши простую функцию на Python для подсчета слов в тексте",
                "model_preferences_id": 7
                # Альтернативный вариант:
                # "provider_id": 1,
                # "model_id": 1
            }
        }


class TokenCountResponseSchema(BaseModel):
    """Схема ответа с информацией о количестве токенов"""
    token_count: int = Field(..., description="Количество токенов")
    estimated: Optional[bool] = False

    class Config:
        json_schema_extra = {
            "example": {
                "token_count": 12,
                "estimated": False
            }
        }


class CategoryErrorResponseSchema(BaseModel):
    """Схема ответа с информацией об ошибке для категорий"""
    detail: str = Field(..., description="Сообщение об ошибке")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Категория с таким именем уже существует"
            }
        }


class ErrorResponseSchema(BaseModel):
    """Схема ответа с информацией об ошибке"""
    error: bool = Field(True, description="Флаг ошибки")
    error_message: str = Field(..., description="Сообщение об ошибке")
    error_type: Optional[str] = Field(None, description="Тип ошибки")
    error_details: Optional[Any] = Field(None, description="Детальная информация об ошибке")

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "error_message": "API ключ для провайдера с ID 1 не найден",
                "error_type": "api_key_not_found",
                "error_details": None
            }
        }


class CategoryWithThreadCountSchema(ThreadCategorySchema):
    """Схема категории треда с количеством тредов"""
    thread_count: int = Field(0, description="Количество тредов в категории")

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "name": "Работа",
                "description": "Треды, связанные с рабочими задачами",
                "color": "#4A90E2",
                "created_at": "2023-08-15T10:00:00",
                "updated_at": "2023-08-15T10:00:00",
                "thread_count": 5
            }
        }


class CategoryListResponseSchema(BaseModel):
    """Схема ответа для списка категорий с дополнительной информацией"""
    categories: List[CategoryWithThreadCountSchema] = Field([], description="Список категорий")
    total_count: int = Field(0, description="Общее количество категорий")

    class Config:
        json_schema_extra = {
            "example": {
                "categories": [
                    {
                        "id": 1,
                        "user_id": 123,
                        "name": "Работа",
                        "description": "Треды, связанные с рабочими задачами",
                        "color": "#4A90E2",
                        "created_at": "2023-08-15T10:00:00",
                        "updated_at": "2023-08-15T10:00:00",
                        "thread_count": 5
                    },
                    {
                        "id": 2,
                        "user_id": 123,
                        "name": "Обучение",
                        "description": "Треды по изучению ИИ",
                        "color": "#E74C3C",
                        "created_at": "2023-08-18T14:30:00",
                        "updated_at": "2023-08-18T14:30:00",
                        "thread_count": 3
                    }
                ],
                "total_count": 2
            }
        }


class StreamResponseItem(BaseModel):
    """Схема для одного элемента потокового ответа"""
    text: Optional[str] = None
    full_response: Optional[str] = None
    tokens: Optional[Dict[str, int]] = None
    cost: Optional[float] = None
    done: Optional[bool] = None
    error: Optional[bool] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    status: Optional[str] = None
    user_message_id: Optional[int] = None
    message_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "status": "connected",
                    "user_message_id": 123
                },
                {
                    "text": "Для работы с OpenAI API"
                },
                {
                    "text": " в Python вы можете использовать"
                },
                {
                    "text": " официальную библиотеку openai."
                },
                {
                    "full_response": "Для работы с OpenAI API в Python вы можете использовать официальную библиотеку openai.",
                    "tokens": {
                        "prompt_tokens": 20,
                        "completion_tokens": 15,
                        "total_tokens": 35
                    },
                    "cost": 0.0005,
                    "done": True
                },
                {
                    "error": True,
                    "error_message": "Соединение с API прервано",
                    "error_type": "connection_error"
                }
            ]
        }
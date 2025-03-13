from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


# Основные схемы запросов к AI
class CompletionRequestSchema(BaseModel):
    """Запрос на создание ответа от AI"""
    provider: str = Field(..., description="Провайдер AI (openai или openai)")
    model: str = Field(..., description="Модель (gpt-4o, gpt-4o, gpt-4o и т.д.)")
    prompt: str = Field(..., description="Текст запроса")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")
    system_prompt: Optional[str] = Field(None, description="Системный промпт (инструкции для модели)")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4o",
                "prompt": "Напиши стихотворение о весне в Санкт-Петербурге",
                "max_tokens": 1500,
                "temperature": 0.8,
                "system_prompt": "Ты талантливый поэт, который пишет красивые стихи в классическом стиле"
            }
        }


class CompletionResponseSchema(BaseModel):
    """Ответ от AI"""
    text: str = Field(..., description="Текст ответа")
    model: str = Field(..., description="Использованная модель")
    provider: str = Field(..., description="Провайдер AI")
    tokens: Dict[str, int] = Field(..., description="Информация о токенах")
    cost: float = Field(..., description="Стоимость запроса в долларах")
    from_cache: Optional[bool] = Field(False, description="Флаг, указывающий, получен ли ответ из кэша")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Над Невой туман рассветный,\nТает снег в объятьях солнца.\nВ Петербурге незаметно\nВесна в права свои вступает...",
                "model": "gpt-4o",
                "provider": "openai",
                "tokens": {
                    "prompt_tokens": 42,
                    "completion_tokens": 220,
                    "total_tokens": 262
                },
                "cost": 0.00786,
                "from_cache": False
            }
        }


class TokenCountRequestSchema(BaseModel):
    """Запрос на подсчет токенов в тексте"""
    provider: str = Field(..., description="Провайдер AI (openai или openai)")
    model: str = Field(..., description="Модель (gpt-4o, gpt-4o, gpt-4o и т.д.)")
    text: str = Field(..., description="Текст для подсчета токенов")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4o",
                "text": "Проанализируй текст Пушкина 'Евгений Онегин' и выдели основные темы произведения"
            }
        }


class TokenCountResponseSchema(BaseModel):
    """Ответ с количеством токенов"""
    token_count: int = Field(..., description="Количество токенов")
    estimated: Optional[bool] = Field(False, description="Флаг, указывающий, является ли подсчет оценочным")

    class Config:
        json_schema_extra = {
            "example": {
                "token_count": 12,
                "estimated": False
            }
        }


class ErrorResponseSchema(BaseModel):
    """Ответ с ошибкой"""
    error: bool = Field(True, description="Флаг ошибки")
    error_message: str = Field(..., description="Текст ошибки")
    error_type: str = Field(..., description="Тип ошибки (not_found, rate_limit, billing, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "error_message": "Превышен лимит запросов. Пожалуйста, повторите попытку позже.",
                "error_type": "rate_limit"
            }
        }


# Схемы для категорий
class ThreadCategoryBaseSchema(BaseModel):
    name: str = Field(..., description="Название категории треда")
    description: Optional[str] = Field(None, description="Описание категории")
    color: Optional[str] = Field(None, description="Цветовая метка для категории (HEX или название)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Учебные проекты",
                "description": "Треды, связанные с учебными заданиями и проектами",
                "color": "#4B0082"
            }
        }


class ThreadCategoryCreateSchema(ThreadCategoryBaseSchema):
    pass


class ThreadCategoryUpdateSchema(ThreadCategoryBaseSchema):
    name: Optional[str] = Field(None, description="Название категории треда")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Проекты по машинному обучению",
                "description": "Треды, посвященные проектам и задачам по ML",
                "color": "#800080"
            }
        }


class ThreadCategorySchema(ThreadCategoryBaseSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 12,
                "user_id": 347,
                "name": "Изучение AI",
                "description": "Беседы с AI на тему искусственного интеллекта и машинного обучения",
                "color": "#008080",
                "created_at": "2024-03-15T12:20:45.123456",
                "updated_at": "2024-03-16T08:15:22.654321"
            }
        }


# Схемы для сообщений
class MessageBaseSchema(BaseModel):
    role: str = Field(..., description="Роль сообщения (user, assistant, system)")
    content: str = Field(..., description="Содержание сообщения")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Какие существуют методы обучения нейронных сетей без учителя?"
            }
        }


class MessageCreateSchema(MessageBaseSchema):
    tokens: Optional[int] = Field(None, description="Количество токенов в сообщении")
    model: Optional[str] = Field(None, description="Модель, используемая для сообщения")
    provider: Optional[str] = Field(None, description="Провайдер ИИ")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Объясни, пожалуйста, как работает алгоритм кластеризации K-means простыми словами",
                "tokens": 16,
                "model": None,
                "provider": None,
                "metadata": {
                    "browser": "Chrome",
                    "os": "Windows 11",
                    "source": "web"
                }
            }
        }


class MessageSchema(MessageBaseSchema):
    id: int
    thread_id: int
    tokens: Optional[int]
    model: Optional[str]
    provider: Optional[str]
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 246,
                "thread_id": 53,
                "role": "assistant",
                "content": "Алгоритм K-means — это метод кластеризации, который разделяет данные на K групп. Представьте, что у вас есть разноцветные точки на бумаге, и вы хотите объединить похожие по цвету точки в группы...",
                "tokens": 256,
                "model": "gpt-4o",
                "provider": "openai",
                "meta_data": {
                    "response_time_ms": 1520,
                    "user_feedback": "helpful"
                },
                "created_at": "2024-03-15T14:30:12.456789"
            }
        }


# Схемы для тредов
class ThreadBaseSchema(BaseModel):
    title: str = Field(..., description="Название треда")
    provider: str = Field(..., description="Провайдер ИИ (openai, openai)")
    model: str = Field(..., description="Модель ИИ (gpt-4o, gpt-4o, и т.д.)")
    category_id: Optional[int] = Field(None, description="ID категории треда")
    is_pinned: Optional[bool] = Field(False, description="Закреплен ли тред")
    is_archived: Optional[bool] = Field(False, description="Архивирован ли тред")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Разработка рекомендательной системы для интернет-магазина",
                "provider": "openai",
                "model": "gpt-4o",
                "category_id": 5,
                "is_pinned": True,
                "is_archived": False
            }
        }


class ThreadCreateSchema(ThreadBaseSchema):
    initial_message: Optional[str] = Field(None, description="Первое сообщение пользователя в треде")
    system_prompt: Optional[str] = Field(None, description="Системный промпт для треда")

    # Параметры генерации ответа
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Анализ данных о продажах за 2023 год",
                "provider": "openai",
                "model": "gpt-4o",
                "category_id": 3,
                "is_pinned": False,
                "is_archived": False,
                "initial_message": "Я хочу проанализировать данные о продажах моего магазина за прошлый год. Как лучше визуализировать сезонные тренды?",
                "system_prompt": "Ты опытный аналитик данных, который помогает пользователю анализировать бизнес-показатели и строить информативные визуализации",
                "max_tokens": 2000,
                "temperature": 0.8
            }
        }


class ThreadUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, description="Название треда")
    category_id: Optional[int] = Field(None, description="ID категории треда")
    is_pinned: Optional[bool] = Field(None, description="Закреплен ли тред")
    is_archived: Optional[bool] = Field(None, description="Архивирован ли тред")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Оптимизация SQL-запросов для высоконагруженного приложения",
                "category_id": 7,
                "is_pinned": True,
                "is_archived": False
            }
        }


class ThreadSummarySchema(ThreadBaseSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime
    category: Optional[ThreadCategorySchema] = None
    message_count: int = Field(..., description="Количество сообщений в треде")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 42,
                "user_id": 156,
                "title": "Обзор алгоритмов для обработки естественного языка",
                "provider": "openai",
                "model": "gpt-4o",
                "category_id": 9,
                "is_pinned": False,
                "is_archived": False,
                "created_at": "2024-02-10T09:15:32.123456",
                "updated_at": "2024-03-15T18:45:10.987654",
                "last_message_at": "2024-03-15T18:45:10.987654",
                "category": {
                    "id": 9,
                    "user_id": 156,
                    "name": "NLP и обработка текста",
                    "description": "Обсуждение технологий и алгоритмов обработки естественного языка",
                    "color": "#008000",
                    "created_at": "2024-01-20T14:22:36.741852",
                    "updated_at": "2024-01-20T14:22:36.741852"
                },
                "message_count": 28
            }
        }


class ThreadSchema(ThreadSummarySchema):
    messages: List[MessageSchema] = Field([], description="Сообщения в треде")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 42,
                "user_id": 156,
                "title": "Обзор алгоритмов для обработки естественного языка",
                "provider": "openai",
                "model": "gpt-4o",
                "category_id": 9,
                "is_pinned": False,
                "is_archived": False,
                "created_at": "2024-02-10T09:15:32.123456",
                "updated_at": "2024-03-15T18:45:10.987654",
                "last_message_at": "2024-03-15T18:45:10.987654",
                "category": {
                    "id": 9,
                    "user_id": 156,
                    "name": "NLP и обработка текста",
                    "description": "Обсуждение технологий и алгоритмов обработки естественного языка",
                    "color": "#008000",
                    "created_at": "2024-01-20T14:22:36.741852",
                    "updated_at": "2024-01-20T14:22:36.741852"
                },
                "message_count": 2,
                "messages": [
                    {
                        "id": 105,
                        "thread_id": 42,
                        "role": "user",
                        "content": "Какие существуют современные алгоритмы для анализа тональности текста?",
                        "tokens": 11,
                        "model": None,
                        "provider": None,
                        "meta_data": {},
                        "created_at": "2024-02-10T09:15:32.123456"
                    },
                    {
                        "id": 106,
                        "thread_id": 42,
                        "role": "assistant",
                        "content": "Современные алгоритмы анализа тональности текста можно разделить на несколько категорий:\n\n1. Основанные на словарях:\n   - VADER (Valence Aware Dictionary and sEntiment Reasoner) - специально разработан для социальных медиа\n   - SentiWordNet - лексический ресурс для анализа мнений\n\n2. Классические методы машинного обучения:\n   - Наивный Байесовский классификатор\n   - SVM (метод опорных векторов)\n   - Логистическая регрессия\n\n3. Глубокое обучение:\n   - RNN и LSTM - учитывают последовательность слов\n   - BERT и его варианты - контекстные модели на основе трансформеров\n   - RoBERTa - оптимизированная версия BERT\n   - XLNet - автореггресивная предварительно обученная модель\n\n4. Ансамблевые методы - комбинируют различные подходы для повышения точности\n\nСамые современные подходы используют предварительно обученные языковые модели трансформеров и тонкую настройку для конкретных задач анализа тональности.",
                        "tokens": 225,
                        "model": "gpt-4o",
                        "provider": "openai",
                        "meta_data": {
                            "response_time_ms": 1856,
                            "prompt_tokens": 15,
                            "completion_tokens": 225
                        },
                        "created_at": "2024-02-10T09:15:40.654321"
                    }
                ]
            }
        }


# Схемы для запросов
class ThreadListParamsSchema(BaseModel):
    skip: Optional[int] = Field(0, description="Пропустить указанное количество тредов")
    limit: Optional[int] = Field(100, description="Максимальное количество возвращаемых тредов")
    category_id: Optional[int] = Field(None, description="Фильтр по ID категории")
    is_archived: Optional[bool] = Field(None, description="Фильтр по архивному статусу")
    is_pinned: Optional[bool] = Field(None, description="Фильтр по закрепленным тредам")
    search: Optional[str] = Field(None, description="Текст для поиска в названиях тредов")

    class Config:
        json_schema_extra = {
            "example": {
                "skip": 20,
                "limit": 50,
                "category_id": 3,
                "is_archived": False,
                "is_pinned": True,
                "search": "нейронные сети"
            }
        }


class BulkThreadActionSchema(BaseModel):
    thread_ids: List[int] = Field(..., description="Список ID тредов для действия")

    class Config:
        json_schema_extra = {
            "example": {
                "thread_ids": [12, 45, 67, 89, 123]
            }
        }


class SendMessageRequestSchema(BaseModel):
    content: str = Field(..., description="Содержание сообщения")
    system_prompt: Optional[str] = Field(None, description="Системный промпт (инструкции для модели)")
    max_tokens: Optional[int] = Field(1000, description="Максимальное количество токенов в ответе")
    temperature: Optional[float] = Field(0.7, description="Температура (случайность) ответа")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Напиши план исследования по теме 'Влияние социальных сетей на психологическое здоровье подростков'",
                "system_prompt": "Ты опытный научный руководитель, специализирующийся на психологии и социологии",
                "max_tokens": 2000,
                "temperature": 0.5
            }
        }

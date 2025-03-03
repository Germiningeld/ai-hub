from typing import List, Dict, Any, Optional
from datetime import date
from pydantic import BaseModel, Field


class DateRangeParamsSchema(BaseModel):
    """Параметры для запроса с диапазоном дат"""
    start_date: Optional[date] = Field(None, description="Начальная дата (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="Конечная дата (YYYY-MM-DD)")


class DailyUsageItemSchema(BaseModel):
    """Использование за один день"""
    date: str = Field(..., description="Дата в формате ISO (YYYY-MM-DD)")
    requests: int = Field(..., description="Количество запросов")
    tokens: int = Field(..., description="Общее количество использованных токенов")
    cost: float = Field(..., description="Стоимость запросов за день")


class ModelUsageItemSchema(BaseModel):
    """Использование одной модели"""
    provider: str = Field(..., description="Провайдер AI")
    model: str = Field(..., description="Название модели")
    requests: int = Field(..., description="Количество запросов к модели")
    tokens: int = Field(..., description="Общее количество использованных токенов")
    cost: float = Field(..., description="Стоимость запросов к модели")


class ProviderSummaryItemSchema(BaseModel):
    """Сводка по провайдеру"""
    provider: str = Field(..., description="Провайдер AI")
    requests: int = Field(..., description="Количество запросов к провайдеру")
    tokens: int = Field(..., description="Общее количество использованных токенов")
    cost: float = Field(..., description="Стоимость запросов к провайдеру")
    models_count: int = Field(..., description="Количество используемых моделей")


class UsageStatisticsResponseSchema(BaseModel):
    """Ответ со статистикой использования за период"""
    start_date: date = Field(..., description="Начальная дата периода")
    end_date: date = Field(..., description="Конечная дата периода")
    total_requests: int = Field(..., description="Общее количество запросов")
    total_tokens: int = Field(..., description="Общее количество использованных токенов")
    total_cost: float = Field(..., description="Общая стоимость запросов")
    daily_usage: List[DailyUsageItemSchema] = Field(..., description="Использование по дням")
    model_usage: List[ModelUsageItemSchema] = Field(..., description="Использование по моделям")
    provider_summary: List[ProviderSummaryItemSchema] = Field(..., description="Сводка по провайдерам")


class PeriodSummarySchema(BaseModel):
    """Сводка использования за период"""
    start_date: Optional[date] = Field(None, description="Начальная дата периода")
    end_date: Optional[date] = Field(None, description="Конечная дата периода")
    requests: int = Field(..., description="Количество запросов")
    tokens: int = Field(..., description="Общее количество использованных токенов")
    cost: float = Field(..., description="Стоимость запросов")


class AllTimeSummarySchema(BaseModel):
    """Сводка использования за все время"""
    requests: int = Field(..., description="Количество запросов")
    tokens: int = Field(..., description="Общее количество использованных токенов")
    cost: float = Field(..., description="Стоимость запросов")


class SavingsSummarySchema(BaseModel):
    """Сводка по экономии"""
    vs_subscription: float = Field(..., description="Экономия по сравнению с подпиской OpenAI Plus")
    subscription_cost: float = Field(..., description="Стоимость подписки OpenAI Plus")


class UsageSummaryResponseSchema(BaseModel):
    """Ответ со сводкой использования"""
    current_month: PeriodSummarySchema = Field(..., description="Использование за текущий месяц")
    last_30_days: PeriodSummarySchema = Field(..., description="Использование за последние 30 дней")
    all_time: AllTimeSummarySchema = Field(..., description="Использование за все время")
    savings: SavingsSummarySchema = Field(..., description="Сводка по экономии")
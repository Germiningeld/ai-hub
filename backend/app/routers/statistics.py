from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta

from app.core.dependencies import get_current_user
from app.db.database import get_async_session
from app.db.models import UserOrm, UsageStatisticsOrm
from app.schemas.statistics import (
    UsageStatisticsResponseSchema,
    DailyUsageItemSchema,
    ModelUsageItemSchema,
    ProviderSummaryItemSchema,
    UsageSummaryResponseSchema,
    DateRangeParamsSchema
)

router = APIRouter()


@router.get("/usage", response_model=UsageStatisticsResponseSchema)
async def get_usage_statistics(
        params: DateRangeParamsSchema = Depends(),
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает статистику использования за указанный период.
    """
    # Получаем даты по умолчанию, если не указаны
    start_date = params.start_date or (datetime.now() - timedelta(days=30)).date()
    end_date = params.end_date or datetime.now().date()

    # Получаем статистику использования
    result = await db.execute(
        select(UsageStatisticsOrm).filter(
            (UsageStatisticsOrm.user_id == current_user.id) &
            (UsageStatisticsOrm.request_date >= start_date) &
            (UsageStatisticsOrm.request_date <= end_date)
        )
    )
    stats = result.scalars().all()

    # Если статистики нет, возвращаем пустой результат
    if not stats:
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "daily_usage": [],
            "model_usage": [],
            "provider_summary": []
        }

    # Подготавливаем данные для ответа
    # Общие суммы
    total_requests = sum(stat.request_count for stat in stats)
    total_tokens = sum(stat.total_tokens for stat in stats)
    total_cost = sum(stat.estimated_cost for stat in stats)

    # Использование по дням
    daily_stats = {}
    for stat in stats:
        day = stat.request_date.isoformat()
        if day not in daily_stats:
            daily_stats[day] = {
                "date": day,
                "requests": 0,
                "tokens": 0,
                "cost": 0
            }

        daily_stats[day]["requests"] += stat.request_count
        daily_stats[day]["tokens"] += stat.total_tokens
        daily_stats[day]["cost"] += stat.estimated_cost

    daily_usage = list(daily_stats.values())
    daily_usage.sort(key=lambda x: x["date"])

    # Использование по моделям
    model_stats = {}
    for stat in stats:
        model_key = f"{stat.provider}-{stat.model}"
        if model_key not in model_stats:
            model_stats[model_key] = {
                "provider": stat.provider,
                "model": stat.model,
                "requests": 0,
                "tokens": 0,
                "cost": 0
            }

        model_stats[model_key]["requests"] += stat.request_count
        model_stats[model_key]["tokens"] += stat.total_tokens
        model_stats[model_key]["cost"] += stat.estimated_cost

    model_usage = list(model_stats.values())
    model_usage.sort(key=lambda x: x["cost"], reverse=True)

    # Сводка по провайдерам
    provider_stats = {}
    for stat in stats:
        if stat.provider not in provider_stats:
            provider_stats[stat.provider] = {
                "provider": stat.provider,
                "requests": 0,
                "tokens": 0,
                "cost": 0,
                "models_count": set()
            }

        provider_stats[stat.provider]["requests"] += stat.request_count
        provider_stats[stat.provider]["tokens"] += stat.total_tokens
        provider_stats[stat.provider]["cost"] += stat.estimated_cost
        provider_stats[stat.provider]["models_count"].add(stat.model)

    provider_summary = []
    for provider, data in provider_stats.items():
        provider_summary.append({
            "provider": provider,
            "requests": data["requests"],
            "tokens": data["tokens"],
            "cost": data["cost"],
            "models_count": len(data["models_count"])
        })

    provider_summary.sort(key=lambda x: x["cost"], reverse=True)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "daily_usage": daily_usage,
        "model_usage": model_usage,
        "provider_summary": provider_summary
    }


@router.get("/summary", response_model=UsageSummaryResponseSchema)
async def get_usage_summary(
        db: AsyncSession = Depends(get_async_session),
        current_user: UserOrm = Depends(get_current_user)
):
    """
    Возвращает краткую сводку использования за последний месяц и всё время.
    """
    # Дата начала текущего месяца
    today = datetime.now().date()
    first_day_of_month = date(today.year, today.month, 1)

    # Статистика за текущий месяц
    result = await db.execute(
        select(
            func.sum(UsageStatisticsOrm.request_count).label("requests"),
            func.sum(UsageStatisticsOrm.total_tokens).label("tokens"),
            func.sum(UsageStatisticsOrm.estimated_cost).label("cost")
        ).filter(
            (UsageStatisticsOrm.user_id == current_user.id) &
            (UsageStatisticsOrm.request_date >= first_day_of_month)
        )
    )
    current_month_stats = result.one()

    # Статистика за всё время
    result = await db.execute(
        select(
            func.sum(UsageStatisticsOrm.request_count).label("requests"),
            func.sum(UsageStatisticsOrm.total_tokens).label("tokens"),
            func.sum(UsageStatisticsOrm.estimated_cost).label("cost")
        ).filter(
            UsageStatisticsOrm.user_id == current_user.id
        )
    )
    all_time_stats = result.one()

    # Статистика за последние 30 дней
    last_30_days = today - timedelta(days=30)
    result = await db.execute(
        select(
            func.sum(UsageStatisticsOrm.request_count).label("requests"),
            func.sum(UsageStatisticsOrm.total_tokens).label("tokens"),
            func.sum(UsageStatisticsOrm.estimated_cost).label("cost")
        ).filter(
            (UsageStatisticsOrm.user_id == current_user.id) &
            (UsageStatisticsOrm.request_date >= last_30_days)
        )
    )
    last_30_days_stats = result.one()

    # Сравнение с подпиской OpenAI Plus ($20/месяц)
    monthly_subscription_cost = 20.0
    current_month_cost = current_month_stats.cost or 0
    savings_vs_subscription = max(0, monthly_subscription_cost - current_month_cost)

    return {
        "current_month": {
            "start_date": first_day_of_month,
            "end_date": today,
            "requests": current_month_stats.requests or 0,
            "tokens": current_month_stats.tokens or 0,
            "cost": current_month_cost
        },
        "last_30_days": {
            "start_date": last_30_days,
            "end_date": today,
            "requests": last_30_days_stats.requests or 0,
            "tokens": last_30_days_stats.tokens or 0,
            "cost": last_30_days_stats.cost or 0
        },
        "all_time": {
            "requests": all_time_stats.requests or 0,
            "tokens": all_time_stats.tokens or 0,
            "cost": all_time_stats.cost or 0
        },
        "savings": {
            "vs_subscription": savings_vs_subscription,
            "subscription_cost": monthly_subscription_cost
        }
    }


# @router.get("/cached-requests", response_model=Dict[str, Any])
# async def get_cached_requests_stats(
#         days: Optional[int] = Query(30, description="Количество дней для анализа"),
#         db: AsyncSession = Depends(get_async_session),
#         current_user: UserOrm = Depends(get_current_user)
# ):
#     """
#     Возвращает статистику по кэшированным запросам и экономии.
#     """
#     # Получаем статистику из сервиса кэширования
#     from app.services.cache_service import get_cache_statistics
#
#     start_date = (datetime.now() - timedelta(days=days)).date()
#     end_date = datetime.now().date()
#
#     # Получаем статистику использования для сравнения
#     result = await db.execute(
#         select(
#             func.sum(UsageStatisticsOrm.total_tokens).label("tokens"),
#             func.sum(UsageStatisticsOrm.estimated_cost).label("cost")
#         ).filter(
#             (UsageStatisticsOrm.user_id == current_user.id) &
#             (UsageStatisticsOrm.request_date >= start_date)
#         )
#     )
#     stats = result.one()
#
#     total_tokens = stats.tokens or 0
#     total_cost = stats.cost or 0
#
#     # Запрашиваем статистику кэширования
#     cache_stats = get_cache_statistics(current_user.id, days)
#
#     # Рассчитываем экономию
#     tokens_saved = cache_stats.get("tokens_saved", 0)
#     cost_saved = cache_stats.get("cost_saved", 0)
#
#     # Процент экономии
#     percent_tokens_saved = (
#                 tokens_saved / (total_tokens + tokens_saved) * 100) if total_tokens + tokens_saved > 0 else 0
#     percent_cost_saved = (cost_saved / (total_cost + cost_saved) * 100) if total_cost + cost_saved > 0 else 0
#
#     return {
#         "period": {
#             "start_date": start_date,
#             "end_date": end_date,
#             "days": days
#         },
#         "cache_hits": cache_stats.get("hits", 0),
#         "cache_misses": cache_stats.get("misses", 0),
#         "hit_ratio": cache_stats.get("hit_ratio", 0),
#         "tokens_saved": tokens_saved,
#         "cost_saved": cost_saved,
#         "percent_tokens_saved": percent_tokens_saved,
#         "percent_cost_saved": percent_cost_saved,
#         "estimated_monthly_savings": (cost_saved / days) * 30 if days > 0 else 0
#     }
import json
import redis
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import CacheEntry, UsageStatistics
from app.core.config import settings
from datetime import date


class CacheService:
    """
    Сервис для кэширования запросов и ответов AI моделей.
    """

    def __init__(self, redis_url: str = settings.REDIS_URL):
        """
        Инициализирует сервис кэширования.

        Args:
            redis_url: URL для подключения к Redis
        """
        self.redis = redis.from_url(redis_url)
        self.ttl = settings.CACHE_TTL  # Время жизни кэша в секундах

    async def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Получает кэшированный ответ по ключу.

        Args:
            cache_key: Ключ кэша

        Returns:
            Словарь с кэшированным ответом или None, если кэш не найден
        """
        cached_data = self.redis.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None

    async def set_cached_response(self,
                                  cache_key: str,
                                  response: Dict[str, Any],
                                  ttl: int = None) -> None:
        """
        Сохраняет ответ в кэш.

        Args:
            cache_key: Ключ кэша
            response: Ответ для кэширования
            ttl: Время жизни кэша в секундах (опционально)
        """
        ttl = ttl or self.ttl
        self.redis.setex(cache_key, ttl, json.dumps(response))

    async def update_cache_statistics(self,
                                      db: Session,
                                      user_id: int,
                                      provider: str,
                                      model: str,
                                      request: str,
                                      tokens_saved: int,
                                      cost_saved: float) -> None:
        """
        Обновляет статистику использования кэша в базе данных.

        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            provider: Провайдер AI (openai, anthropic)
            model: Название модели
            request: Текст запроса
            tokens_saved: Количество сэкономленных токенов
            cost_saved: Сэкономленная стоимость
        """
        # Проверяем существование кэша для данного запроса
        cache_entry = db.query(CacheEntry).filter(
            CacheEntry.user_id == user_id,
            CacheEntry.provider == provider,
            CacheEntry.model == model,
            CacheEntry.request_hash == cache_key
        ).first()

        if cache_entry:
            # Обновляем существующую запись
            cache_entry.hit_count += 1
            cache_entry.tokens_saved += tokens_saved
            cache_entry.cost_saved += cost_saved
            cache_entry.last_accessed_at = func.now()
        else:
            # Создаем новую запись
            cache_entry = CacheEntry(
                user_id=user_id,
                provider=provider,
                model=model,
                request_hash=cache_key,
                request=request,
                response=json.dumps(response),
                tokens_saved=tokens_saved,
                cost_saved=cost_saved,
                hit_count=1
            )
            db.add(cache_entry)

        # Обновляем общую статистику использования
        today = date.today()

        usage_stat = db.query(UsageStatistics).filter(
            UsageStatistics.user_id == user_id,
            UsageStatistics.provider == provider,
            UsageStatistics.model == model,
            UsageStatistics.request_date == today
        ).first()

        if usage_stat:
            usage_stat.cached_requests += 1
            usage_stat.tokens_saved += tokens_saved
            usage_stat.cost_saved += cost_saved
        else:
            usage_stat = UsageStatistics(
                user_id=user_id,
                provider=provider,
                model=model,
                request_date=today,
                cached_requests=1,
                tokens_saved=tokens_saved,
                cost_saved=cost_saved
            )
            db.add(usage_stat)

        db.commit()
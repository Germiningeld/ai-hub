from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.base_ai_service import BaseAIService
from app.services.openai_service import OpenAIService
from app.services.anthropic_service import AnthropicService
from app.db.models import ApiKeyOrm


class AIServiceFactory:
    """
    Фабрика для создания сервисов AI.
    """

    @staticmethod
    async def get_service(provider: str, api_key: str) -> BaseAIService:
        """
        Создает и возвращает сервис AI для указанного провайдера.

        Args:
            provider: Имя провайдера ('openai' или 'anthropic')
            api_key: API ключ для провайдера

        Returns:
            Экземпляр сервиса AI
        """
        if provider.lower() == "openai":
            return OpenAIService(api_key)
        elif provider.lower() == "anthropic":
            return AnthropicService(api_key)
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {provider}")

    @classmethod
    async def create_service_for_user(cls,
                                    db: AsyncSession,
                                    user_id: int,
                                    provider: str) -> Optional[BaseAIService]:
        """
        Создает сервис AI для пользователя на основе его API ключей.

        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            provider: Имя провайдера ('openai' или 'anthropic')

        Returns:
            Экземпляр сервиса AI или None, если ключ не найден
        """
        # Ищем активный API ключ пользователя для указанного провайдера
        result = await db.execute(
            select(ApiKeyOrm).filter(
                ApiKeyOrm.user_id == user_id,
                ApiKeyOrm.provider == provider,
                ApiKeyOrm.is_active == True
            )
        )
        api_key_record = result.scalars().first()

        if not api_key_record:
            return None

        return await cls.get_service(provider, api_key_record.api_key)
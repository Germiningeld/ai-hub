from typing import Optional, Type, Dict, Any, List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
import importlib
import logging

from app.services.base_ai_service import BaseAIService
from app.db.models import (
    ApiKeyOrm, ProviderOrm, AIModelOrm, UserOrm, ModelPreferencesOrm
)


class AIServiceException(Exception):
    """Базовое исключение для ошибок связанных с AI сервисами"""
    pass


class ProviderNotFoundException(AIServiceException):
    """Исключение для случаев, когда провайдер не найден"""
    pass


class APIKeyNotFoundException(AIServiceException):
    """Исключение для случаев, когда API ключ не найден"""
    pass


class InactiveProviderException(AIServiceException):
    """Исключение для случаев, когда провайдер неактивен"""
    pass


class ServiceCreationException(AIServiceException):
    """Исключение для ошибок при создании сервиса"""
    pass


class AIServiceFactory:
    """
    Фабрика для создания сервисов AI.

    Эта фабрика управляет созданием сервисов для различных провайдеров AI
    и поддерживает кэширование сервисов для оптимизации производительности.
    """

    _service_cache: Dict[str, BaseAIService] = {}
    _logger = logging.getLogger("ai_service_factory")

    @classmethod
    def clear_cache(cls):
        """Очищает кэш сервисов"""
        cls._service_cache.clear()
        cls._logger.info("Кэш сервисов очищен")

    @classmethod
    def get_cache_key(cls, api_key_id: Optional[int] = None,
                      user_id: Optional[int] = None,
                      provider_id: Optional[int] = None) -> str:
        """
        Создает ключ для кэша сервисов

        Args:
            api_key_id: ID API ключа
            user_id: ID пользователя
            provider_id: ID провайдера

        Returns:
            Строка ключа кэша
        """
        if api_key_id:
            return f"key_{api_key_id}"
        if user_id and provider_id:
            return f"user_{user_id}_provider_{provider_id}"
        raise ValueError("Необходимо указать либо api_key_id, либо комбинацию user_id и provider_id")

    @classmethod
    async def get_service_by_key_id(cls,
                                    db: AsyncSession,
                                    api_key_id: int,
                                    use_cache: bool = True) -> BaseAIService:
        """
        Создает сервис AI на основе ID API ключа.
        """
        cache_key = cls.get_cache_key(api_key_id=api_key_id)

        # Проверяем кэш
        if use_cache and cache_key in cls._service_cache:
            cls._logger.debug(f"Используется кэшированный сервис для API ключа #{api_key_id}")
            return cls._service_cache[cache_key]

        # Получаем API ключ из базы данных с загрузкой связанного провайдера
        result = await db.execute(
            select(ApiKeyOrm).options(
                selectinload(ApiKeyOrm.provider)
            ).filter(
                ApiKeyOrm.id == api_key_id,
                ApiKeyOrm.is_active == True
            )
        )
        api_key = result.scalars().first()

        if not api_key:
            raise APIKeyNotFoundException(f"API ключ с ID {api_key_id} не найден или неактивен")

        # Проверяем активность провайдера
        if not api_key.provider.is_active:
            raise InactiveProviderException(f"Провайдер {api_key.provider.name} неактивен")

        # Создаем сервис
        try:
            service_class = api_key.provider.get_service_class()
            service = service_class(api_key.api_key)

            # Кэшируем сервис
            if use_cache:
                cls._service_cache[cache_key] = service

            return service

        except Exception as e:
            cls._logger.error(f"Ошибка при создании сервиса для API ключа #{api_key_id}: {str(e)}")
            raise ServiceCreationException(f"Не удалось создать сервис: {str(e)}")

    @classmethod
    async def get_service_by_user_and_model(cls,
                                            db: AsyncSession,
                                            user_id: int,
                                            model_id_or_code: Union[int, str],
                                            use_cache: bool = True) -> BaseAIService:
        """
        Создает сервис AI для пользователя на основе ID или кода модели.

        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            model_id_or_code: ID модели или её код (например, 'gpt-4')
            use_cache: Использовать ли кэш

        Returns:
            Сервис AI

        Raises:
            ProviderNotFoundException: Если провайдер не найден
            APIKeyNotFoundException: Если API ключ не найден
            ServiceCreationException: При ошибке создания сервиса
        """
        model = None

        # Обрабатываем случай, когда передан код модели
        if isinstance(model_id_or_code, str):
            # Получаем модель по коду
            result = await db.execute(
                select(AIModelOrm).filter(AIModelOrm.code == model_id_or_code)
            )
            model = result.scalars().first()

            if not model:
                raise ProviderNotFoundException(f"Модель с кодом {model_id_or_code} не найдена")
        else:
            # Получаем модель по ID
            result = await db.execute(
                select(AIModelOrm).filter(AIModelOrm.id == model_id_or_code)
            )
            model = result.scalars().first()

            if not model:
                raise ProviderNotFoundException(f"Модель с ID {model_id_or_code} не найдена")

        # Получаем сервис по провайдеру модели
        return await cls.get_service_by_user_and_provider(
            db, user_id, model.provider_id, use_cache
        )

    @classmethod
    async def get_service_by_user_and_provider(cls,
                                              db: AsyncSession,
                                              user_id: int,
                                              provider_id: int,
                                              use_cache: bool = True) -> BaseAIService:
        """
        Создает сервис AI для пользователя на основе ID провайдера.

        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            provider_id: ID провайдера
            use_cache: Использовать ли кэш

        Returns:
            Сервис AI

        Raises:
            ProviderNotFoundException: Если провайдер не найден
            APIKeyNotFoundException: Если API ключ не найден
            ServiceCreationException: При ошибке создания сервиса
        """
        cache_key = cls.get_cache_key(user_id=user_id, provider_id=provider_id)

        # Проверяем кэш
        if use_cache and cache_key in cls._service_cache:
            cls._logger.debug(f"Используется кэшированный сервис для пользователя #{user_id} и провайдера #{provider_id}")
            return cls._service_cache[cache_key]

        # Проверяем существование провайдера
        provider_result = await db.execute(
            select(ProviderOrm).filter(
                (ProviderOrm.id == provider_id) &
                (ProviderOrm.is_active == True)
            )
        )
        provider = provider_result.scalars().first()

        if not provider:
            raise ProviderNotFoundException(f"Провайдер с ID {provider_id} не найден или неактивен")

        # Получаем активный API ключ пользователя для указанного провайдера
        api_key_result = await db.execute(
            select(ApiKeyOrm).filter(
                (ApiKeyOrm.user_id == user_id) &
                (ApiKeyOrm.provider_id == provider_id) &
                (ApiKeyOrm.is_active == True)
            ).order_by(ApiKeyOrm.created_at.desc())
        )
        api_key = api_key_result.scalars().first()

        if not api_key:
            raise APIKeyNotFoundException(f"API ключ для провайдера {provider.name} (ID: {provider_id}) не найден")

        # Создаем сервис
        try:
            service_class = provider.get_service_class()
            service = service_class(api_key.api_key)

            # Кэшируем сервис
            if use_cache:
                cls._service_cache[cache_key] = service

            return service

        except Exception as e:
            cls._logger.error(f"Ошибка при создании сервиса для провайдера {provider.name} (ID: {provider_id}): {str(e)}")
            raise ServiceCreationException(f"Не удалось создать сервис: {str(e)}")

    @classmethod
    async def get_service_by_preference(cls,
                                        db: AsyncSession,
                                        preference_id: int,
                                        use_cache: bool = True) -> BaseAIService:
        """
        Создает сервис AI на основе ID предпочтений модели.

        Args:
            db: Сессия базы данных
            preference_id: ID предпочтений модели
            use_cache: Использовать ли кэш

        Returns:
            Сервис AI

        Raises:
            ProviderNotFoundException: Если предпочтения не найдены
            APIKeyNotFoundException: Если API ключ не найден
            ServiceCreationException: При ошибке создания сервиса
        """
        # Получаем предпочтения для определения пользователя и провайдера
        result = await db.execute(
            select(ModelPreferencesOrm).filter(ModelPreferencesOrm.id == preference_id)
        )
        preference = result.scalars().first()

        if not preference:
            raise ProviderNotFoundException(f"Предпочтения модели с ID {preference_id} не найдены")

        # Получаем сервис по пользователю и провайдеру
        return await cls.get_service_by_user_and_provider(
            db, preference.user_id, preference.provider_id, use_cache
        )

    @classmethod
    async def get_active_providers(cls, db: AsyncSession) -> List[ProviderOrm]:
        """
        Получает список всех активных провайдеров.

        Args:
            db: Сессия базы данных

        Returns:
            Список активных провайдеров
        """
        result = await db.execute(
            select(ProviderOrm).filter(ProviderOrm.is_active == True)
        )
        return result.scalars().all()

    @classmethod
    async def get_available_providers_for_user(cls,
                                               db: AsyncSession,
                                               user_id: int) -> List[ProviderOrm]:
        """
        Получает список провайдеров, доступных для конкретного пользователя
        (для которых у него есть API ключи).

        Args:
            db: Сессия базы данных
            user_id: ID пользователя

        Returns:
            Список доступных провайдеров
        """
        # Подзапрос для определения провайдеров с активными ключами
        subquery = select(ApiKeyOrm.provider_id).filter(
            ApiKeyOrm.user_id == user_id,
            ApiKeyOrm.is_active == True
        ).distinct()

        # Основной запрос
        result = await db.execute(
            select(ProviderOrm).filter(
                ProviderOrm.id.in_(subquery),
                ProviderOrm.is_active == True
            )
        )
        return result.scalars().all()

    @classmethod
    async def detect_provider_for_key(cls,
                                      db: AsyncSession,
                                      api_key: str) -> Optional[ProviderOrm]:
        """
        Определяет провайдера по формату API ключа.

        Args:
            db: Сессия базы данных
            api_key: API ключ

        Returns:
            Провайдер или None, если не удалось определить
        """
        # Определяем код провайдера по формату ключа
        provider_code = ApiKeyOrm.detect_provider(api_key)

        if not provider_code:
            return None

        # Ищем соответствующего провайдера в базе данных
        result = await db.execute(
            select(ProviderOrm).filter(
                ProviderOrm.code == provider_code,
                ProviderOrm.is_active == True
            )
        )
        return result.scalars().first()

    @classmethod
    async def create_service_from_string_key(cls,
                                             db: AsyncSession,
                                             api_key: str) -> Optional[BaseAIService]:
        """
        Создает сервис напрямую из API ключа, определяя провайдера.

        Args:
            db: Сессия базы данных
            api_key: API ключ

        Returns:
            Сервис AI или None, если не удалось определить провайдера

        Raises:
            ServiceCreationException: При ошибке создания сервиса
        """
        # Определяем провайдера по ключу
        provider = await cls.detect_provider_for_key(db, api_key)

        if not provider:
            cls._logger.warning(f"Не удалось определить провайдера для API ключа")
            return None

        # Создаем сервис
        try:
            service_class = provider.get_service_class()
            return service_class(api_key)
        except Exception as e:
            cls._logger.error(f"Ошибка при создании сервиса для провайдера {provider.name} (ID: {provider.id}): {str(e)}")
            raise ServiceCreationException(f"Не удалось создать сервис: {str(e)}")
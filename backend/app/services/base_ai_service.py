from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseAIService(ABC):
    """
    Абстрактный базовый класс для всех AI сервисов.
    Определяет общий интерфейс и вспомогательные методы.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def generate_completion(self,
                                  prompt: str,
                                  model: str,
                                  max_tokens: int = 1000,
                                  temperature: float = 0.7,
                                  **kwargs) -> Dict[str, Any]:
        """
        Генерирует ответ на основе промпта.

        Args:
            prompt: Текст запроса
            model: Имя модели
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (случайность) ответа
            **kwargs: Дополнительные параметры для API

        Returns:
            Словарь с ответом и метаданными
        """
        pass

    async def generate_completion_with_context(self,
                                               context: List[Dict[str, str]],
                                               model: str,
                                               max_tokens: int = 1000,
                                               temperature: float = 0.7,
                                               **kwargs) -> Dict[str, Any]:
        """
        Генерирует ответ на основе контекста диалога.

        Этот метод предназначен для использования в тредах, когда нужно
        учитывать предыдущие сообщения. Каждый сервис должен реализовать
        свою версию, но эта реализация по умолчанию просто берет последнее
        сообщение пользователя.

        Args:
            context: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
            model: Имя модели
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (случайность) ответа
            **kwargs: Дополнительные параметры для API

        Returns:
            Словарь с ответом и метаданными
        """
        # По умолчанию извлекаем последнее сообщение пользователя как промпт
        user_messages = [msg for msg in context if msg.get("role") == "user"]
        if not user_messages:
            return {
                "error": True,
                "error_message": "В контексте нет сообщений пользователя",
                "error_type": "invalid_context"
            }

        last_user_message = user_messages[-1]["content"]

        # Извлекаем системный промпт, если есть
        system_messages = [msg for msg in context if msg.get("role") == "system"]
        system_prompt = system_messages[0]["content"] if system_messages else None

        # Вызываем обычный generate_completion с последним сообщением пользователя
        return await self.generate_completion(
            prompt=last_user_message,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
            **kwargs
        )

    @abstractmethod
    async def calculate_tokens(self, text: str, model: str) -> Dict[str, int]:
        """
        Рассчитывает количество токенов в тексте для указанной модели.

        Args:
            text: Текст для подсчета токенов
            model: Имя модели

        Returns:
            Словарь с количеством токенов
        """
        pass

    @abstractmethod
    async def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Рассчитывает стоимость запроса на основе токенов.

        Args:
            prompt_tokens: Количество токенов в запросе
            completion_tokens: Количество токенов в ответе
            model: Имя модели

        Returns:
            Стоимость в долларах
        """
        pass

    @abstractmethod
    async def update_usage_statistics(self,
                                      db,
                                      user_id: int,
                                      tokens_data: Dict[str, int],
                                      model: str,
                                      cost: float) -> None:
        """
        Обновляет статистику использования API в базе данных.

        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            tokens_data: Данные о токенах
            model: Название модели
            cost: Стоимость запроса
        """
        pass
import asyncio
import anthropic
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Dict, Any, List, Optional

from app.services.base_ai_service import BaseAIService
from app.core.config import settings
from app.db.models import UsageStatistics
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy.exc import SQLAlchemyError


class AnthropicService(BaseAIService):
    """
    Сервис для работы с API Anthropic (Claude).
    """

    def __init__(self, api_key: str):
        """
        Инициализирует сервис Anthropic.

        Args:
            api_key: Ключ API Anthropic
        """
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)

        # Словарь с тарифами на токены для разных моделей Claude
        # Формат: {модель: (стоимость_input_токенов, стоимость_output_токенов)}
        self.token_pricing = {
            "claude-3-opus": (15.0 / 1000000, 75.0 / 1000000),  # $15 за 1M токенов ввода, $75 за 1M токенов вывода
            "claude-3-sonnet": (3.0 / 1000000, 15.0 / 1000000),  # $3 за 1M токенов ввода, $15 за 1M токенов вывода
            "claude-3-haiku": (0.25 / 1000000, 1.25 / 1000000),  # $0.25 за 1M токенов ввода, $1.25 за 1M токенов вывода
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((anthropic.APIError, anthropic.APIConnectionError, anthropic.RateLimitError))
    )
    async def generate_completion(self,
                                  prompt: str,
                                  model: str = "claude-3-sonnet",
                                  max_tokens: int = 1000,
                                  temperature: float = 0.7,
                                  **kwargs) -> Dict[str, Any]:
        """
        Генерирует ответ на основе промпта с использованием Anthropic API.

        Args:
            prompt: Текст запроса
            model: Имя модели
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (случайность) ответа
            **kwargs: Дополнительные параметры для API

        Returns:
            Словарь с ответом и метаданными
        """
        # Формируем системный промпт
        system_prompt = kwargs.get("system_prompt", "")

        # Выполняем запрос к API
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **{k: v for k, v in kwargs.items() if k not in ["system_prompt"]}
            )

            # Извлекаем ответ
            answer = response.content[0].text

            # Собираем данные о токенах
            tokens_data = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }

            # Рассчитываем стоимость запроса
            cost = await self.calculate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens,
                model
            )

            # Формируем результат
            result = {
                "text": answer,
                "tokens": tokens_data,
                "cost": cost,
                "model": model,
                "provider": "anthropic"
            }

            return result

        except anthropic.APIError as e:
            # Обрабатываем ошибки API
            error_message = str(e)
            if "rate_limit" in error_message.lower():
                error_type = "rate_limit"
            elif "billing" in error_message.lower():
                error_type = "billing"
            else:
                error_type = "routers"

            return {
                "error": True,
                "error_message": error_message,
                "error_type": error_type
            }

    async def calculate_tokens(self, text: str, model: str = "claude-3-sonnet") -> Dict[str, int]:
        """
        Рассчитывает примерное количество токенов в тексте для моделей Claude.

        Args:
            text: Текст для подсчета токенов
            model: Имя модели

        Returns:
            Словарь с количеством токенов
        """
        # Для Claude используем приблизительную оценку, поскольку нет официальной библиотеки для подсчета
        # В среднем 1 токен = 4 символа для английского текста
        # Для других языков и символов пропорция может отличаться
        token_count = len(text) // 4

        return {
            "token_count": token_count,
            "estimated": True  # Флаг, указывающий, что это оценка
        }

    async def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Рассчитывает стоимость запроса на основе токенов для моделей Claude.

        Args:
            prompt_tokens: Количество токенов в запросе
            completion_tokens: Количество токенов в ответе
            model: Имя модели

        Returns:
            Стоимость в долларах
        """
        # Получаем тарифы для указанной модели или используем тарифы claude-3-sonnet по умолчанию
        input_price, output_price = self.token_pricing.get(
            model, self.token_pricing["claude-3-sonnet"]
        )

        # Рассчитываем стоимость
        input_cost = prompt_tokens * input_price
        output_cost = completion_tokens * output_price
        total_cost = input_cost + output_cost

        return total_cost

    async def update_usage_statistics(self,
                                      db: Session,
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
        try:
            today = date.today()

            # Ищем или создаем запись статистики за сегодня
            usage_stat = db.query(UsageStatistics).filter(
                UsageStatistics.user_id == user_id,
                UsageStatistics.provider == "anthropic",
                UsageStatistics.model == model,
                UsageStatistics.request_date == today
            ).first()

            if usage_stat:
                # Обновляем существующую запись
                usage_stat.request_count += 1
                usage_stat.tokens_prompt += tokens_data.get("prompt_tokens", 0)
                usage_stat.tokens_completion += tokens_data.get("completion_tokens", 0)
                usage_stat.total_tokens += tokens_data.get("total_tokens", 0)
                usage_stat.estimated_cost += cost
            else:
                # Создаем новую запись
                new_stat = UsageStatistics(
                    user_id=user_id,
                    provider="anthropic",
                    model=model,
                    request_date=today,
                    request_count=1,
                    tokens_prompt=tokens_data.get("prompt_tokens", 0),
                    tokens_completion=tokens_data.get("completion_tokens", 0),
                    total_tokens=tokens_data.get("total_tokens", 0),
                    estimated_cost=cost
                )
                db.add(new_stat)

            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            # Логирование ошибки
            print(f"Error updating usage statistics: {str(e)}")
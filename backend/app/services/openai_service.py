import asyncio
import tiktoken
from typing import Dict, Any, List, Optional
import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.services.base_ai_service import BaseAIService
from app.core.config import settings
from app.db.models import UsageStatistics
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy.exc import SQLAlchemyError


class OpenAIService(BaseAIService):
    """
    Сервис для работы с API OpenAI.
    """

    def __init__(self, api_key: str):
        """
        Инициализирует сервис OpenAI.

        Args:
            api_key: Ключ API OpenAI
        """
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)

        # Словарь с тарифами на токены для разных моделей
        # Формат: {модель: (стоимость_input_токенов, стоимость_output_токенов)}
        self.token_pricing = {
            "gpt-4": (0.03 / 1000, 0.06 / 1000),  # $0.03 за 1K токенов ввода, $0.06 за 1K токенов вывода
            "gpt-4-turbo": (0.01 / 1000, 0.03 / 1000),
            "gpt-3.5-turbo": (0.0015 / 1000, 0.002 / 1000),
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError))
    )
    async def generate_completion(self,
                                  prompt: str,
                                  model: str = "gpt-3.5-turbo",
                                  max_tokens: int = 1000,
                                  temperature: float = 0.7,
                                  **kwargs) -> Dict[str, Any]:
        """
        Генерирует ответ на основе промпта с использованием OpenAI API.

        Args:
            prompt: Текст запроса
            model: Имя модели
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (случайность) ответа
            **kwargs: Дополнительные параметры для API

        Returns:
            Словарь с ответом и метаданными
        """
        # Формируем сообщения для Chat API
        messages = [{"role": "user", "content": prompt}]

        # Если указан системный промпт, добавляем его
        if "system_prompt" in kwargs:
            messages.insert(0, {"role": "system", "content": kwargs["system_prompt"]})

        # Выполняем запрос к API
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **{k: v for k, v in kwargs.items() if k not in ["system_prompt"]}
            )

            # Извлекаем ответ
            answer = response.choices[0].message.content

            # Собираем данные о токенах
            tokens_data = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            # Рассчитываем стоимость запроса
            cost = await self.calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                model
            )

            # Формируем результат
            result = {
                "text": answer,
                "tokens": tokens_data,
                "cost": cost,
                "model": model,
                "provider": "openai"
            }

            return result

        except openai.APIError as e:
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

    async def calculate_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> Dict[str, int]:
        """
        Рассчитывает количество токенов в тексте для указанной модели OpenAI.

        Args:
            text: Текст для подсчета токенов
            model: Имя модели

        Returns:
            Словарь с количеством токенов
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            token_count = len(encoding.encode(text))

            return {
                "token_count": token_count
            }
        except Exception as e:
            # Если не удалось определить энкодинг для указанной модели,
            # используем cl100k_base (наиболее универсальный)
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                token_count = len(encoding.encode(text))

                return {
                    "token_count": token_count
                }
            except Exception as e:
                # В крайнем случае используем приблизительную оценку
                # (в среднем 4 символа = 1 токен)
                token_count = len(text) // 4

                return {
                    "token_count": token_count,
                    "estimated": True
                }

    async def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Рассчитывает стоимость запроса на основе токенов для моделей OpenAI.

        Args:
            prompt_tokens: Количество токенов в запросе
            completion_tokens: Количество токенов в ответе
            model: Имя модели

        Returns:
            Стоимость в долларах
        """
        # Получаем тарифы для указанной модели или используем тарифы gpt-3.5-turbo по умолчанию
        input_price, output_price = self.token_pricing.get(
            model, self.token_pricing["gpt-3.5-turbo"]
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
                UsageStatistics.provider == "openai",
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
                    provider="openai",
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
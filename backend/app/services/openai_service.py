import httpx
import asyncio
import tiktoken
from typing import Dict, Any, List, Optional, Tuple
import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy import select

from app.services.base_ai_service import BaseAIService
from app.core.settings import settings
from app.db.models import UsageStatisticsOrm
from sqlalchemy.ext.asyncio import AsyncSession
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
                                  system_prompt: Optional[str] = None,
                                  stream=False,
                                  **kwargs) -> Dict[str, Any]:
        """
        Генерирует ответ на основе промпта с использованием API OpenAI.

        Args:
            prompt: Текст запроса
            model: Имя модели OpenAI
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (случайность) ответа
            system_prompt: Системный промпт (инструкции для модели)
            stream: Флаг потоковой генерации
            **kwargs: Дополнительные параметры для API

        Returns:
            Словарь с ответом и метаданными
        """
        if stream:
            return self.stream_completion(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=system_prompt,
                **kwargs
            )

        # Создаем базовые сообщения
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            # Выполняем запрос с полными параметрами
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # Получаем информацию о токенах
            tokens_data = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            # Рассчитываем стоимость
            cost = await self.calculate_cost(
                tokens_data["prompt_tokens"],
                tokens_data["completion_tokens"],
                model
            )

            return {
                "text": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "tokens": tokens_data,
                "cost": cost
            }
        except Exception as e:
            error_info = {
                "error": True,
                "error_message": str(e),
                "error_type": type(e).__name__,
                "error_doc": str(getattr(e, "__doc__", "No documentation")),
                "error_args": str(getattr(e, "args", [])),
            }
            return error_info

    async def generate_completion_with_context(self,
                                               context: List[Dict[str, str]],
                                               model: str = "gpt-3.5-turbo",
                                               max_tokens: int = 1000,
                                               temperature: float = 0.7,
                                               stream=False,
                                               **kwargs) -> Dict[str, Any]:
        """
        Генерирует ответ на основе контекста диалога с использованием API OpenAI.

        Args:
            context: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
            model: Имя модели OpenAI
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура (случайность) ответа
            stream: Флаг потоковой генерации
            **kwargs: Дополнительные параметры для API

        Returns:
            Словарь с ответом и метаданными
        """
        if stream:
            return self.stream_completion_with_context(
                context=context,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

        try:
            # OpenAI API уже поддерживает формат сообщений, поэтому просто передаем контекст
            response = await self.client.chat.completions.create(
                model=model,
                messages=context,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # Получаем информацию о токенах
            tokens_data = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            # Рассчитываем стоимость
            cost = await self.calculate_cost(
                tokens_data["prompt_tokens"],
                tokens_data["completion_tokens"],
                model
            )

            return {
                "text": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "tokens": tokens_data,
                "cost": cost
            }
        except Exception as e:
            error_info = {
                "error": True,
                "error_message": str(e),
                "error_type": type(e).__name__,
                "error_doc": str(getattr(e, "__doc__", "No documentation")),
                "error_args": str(getattr(e, "args", [])),
            }
            return error_info

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

    def count_tokens_for_messages(self, messages: List[Dict[str, str]], model: str) -> int:
        """
        Подсчитывает количество токенов для сообщений чата.

        Args:
            messages: Список сообщений
            model: Модель для подсчета

        Returns:
            Количество токенов
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 3  # каждое сообщение начинается с <im_start>{role/name}\n
        tokens_per_name = 1  # если есть имя, формат: {name}\n

        # Подсчет токенов
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # только имя потребляет токены_на_имя
                    num_tokens += tokens_per_name

        # Каждый ответ начинается с <im_start>assistant
        num_tokens += 3

        return num_tokens

    async def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str,
                             model_preference_id: Optional[int] = None, is_cached: bool = False) -> Tuple[
        float, Optional[Dict]]:
        """
        Рассчитывает стоимость запроса на основе токенов для моделей.

        Args:
            prompt_tokens: Количество токенов в запросе
            completion_tokens: Количество токенов в ответе
            model: Имя модели (используется как fallback)
            model_preference_id: ID настроек модели в базе данных
            is_cached: Был ли ответ получен из кэша

        Returns:
            Tuple[float, Optional[Dict]]: Стоимость в долларах и информация об использованной модели цен
        """
        # Данные для отладки и мониторинга
        pricing_info = None

        # Если указан ID настроек модели, пытаемся получить ценовую информацию из базы данных
        if model_preference_id:
            async with self.db_session() as db:
                model_pref = await db.execute(
                    select(ModelPreferencesOrm).filter(ModelPreferencesOrm.id == model_preference_id)
                )
                model_pref = model_pref.scalar_one_or_none()

                if model_pref:
                    pricing_info = {
                        "source": "db",
                        "model_id": model_pref.id,
                        "model_name": model_pref.model,
                        "provider": model_pref.provider
                    }

                    # Определяем стоимость входных токенов (учитываем кэширование, если применимо)
                    input_price = 0.0
                    if prompt_tokens > 0:
                        if is_cached and model_pref.cached_input_cost is not None:
                            input_price = model_pref.cached_input_cost / 1000
                            pricing_info["input_price_source"] = "cached_rate"
                        elif model_pref.input_cost is not None:
                            input_price = model_pref.input_cost / 1000
                            pricing_info["input_price_source"] = "standard_rate"

                    # Определяем стоимость выходных токенов
                    output_price = 0.0
                    if completion_tokens > 0 and model_pref.output_cost is not None:
                        output_price = model_pref.output_cost / 1000
                        pricing_info["output_price_source"] = "standard_rate"

                    # Если у модели есть цены, используем их для расчета
                    if input_price > 0 or output_price > 0:
                        pricing_info["input_price"] = input_price
                        pricing_info["output_price"] = output_price

                        # Рассчитываем стоимость
                        input_cost = prompt_tokens * input_price
                        output_cost = completion_tokens * output_price
                        total_cost = input_cost + output_cost

                        pricing_info["input_cost"] = input_cost
                        pricing_info["output_cost"] = output_cost
                        pricing_info["total_cost"] = total_cost

                        return total_cost, pricing_info

        # Если не удалось получить цены из настроек модели, используем стандартные цены
        # Получаем тарифы для указанной модели или используем тарифы по умолчанию
        input_price, output_price = self.token_pricing.get(
            model, self.token_pricing["gpt-3.5-turbo"]
        )

        pricing_info = {
            "source": "default",
            "model": model,
            "input_price": input_price,
            "output_price": output_price
        }

        # Рассчитываем стоимость
        input_cost = prompt_tokens * input_price
        output_cost = completion_tokens * output_price
        total_cost = input_cost + output_cost

        pricing_info["input_cost"] = input_cost
        pricing_info["output_cost"] = output_cost
        pricing_info["total_cost"] = total_cost

        return total_cost, pricing_info
    async def update_usage_statistics(self,
                                      db: AsyncSession,
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
            query = select(UsageStatisticsOrm).filter(
                UsageStatisticsOrm.user_id == user_id,
                UsageStatisticsOrm.provider == "openai",
                UsageStatisticsOrm.model == model,
                UsageStatisticsOrm.request_date == today
            )

            result = await db.execute(query)
            usage_stat = result.scalars().first()

            if usage_stat:
                # Обновляем существующую запись
                usage_stat.request_count += 1
                usage_stat.tokens_prompt += tokens_data.get("prompt_tokens", 0)
                usage_stat.tokens_completion += tokens_data.get("completion_tokens", 0)
                usage_stat.total_tokens += tokens_data.get("total_tokens", 0)
                usage_stat.estimated_cost += cost
            else:
                # Создаем новую запись
                new_stat = UsageStatisticsOrm(
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

            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            # Логирование ошибки
            print(f"Error updating usage statistics: {str(e)}")

    async def stream_completion(self,
                                prompt: str,
                                model: str = "gpt-3.5-turbo",
                                max_tokens: int = 1000,
                                temperature: float = 0.7,
                                system_prompt: Optional[str] = None,
                                **kwargs):
        """
        Генерирует ответ в потоковом режиме без контекста.

        Args:
            prompt: Текст запроса
            model: Модель
            max_tokens: Максимальное количество токенов
            temperature: Температура
            system_prompt: Системный промпт

        Yields:
            Куски ответа и данные о токенах/стоимости
        """
        # Создаем сообщения
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        full_response = ""
        prompt_tokens = self.count_tokens_for_messages(messages, model)

        try:
            # Запрашиваем потоковый ответ
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )

            # Собираем ответ по кускам
            async for chunk in stream:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        yield {"text": content}

            # Подсчет токенов и стоимости по завершении
            completion_tokens = len(tiktoken.encoding_for_model(model).encode(full_response))
            total_tokens = prompt_tokens + completion_tokens

            tokens_data = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }

            cost = await self.calculate_cost(
                prompt_tokens,
                completion_tokens,
                model
            )

            yield {"tokens": tokens_data, "cost": cost}

        except Exception as e:
            yield {"error": True, "error_message": str(e)}

    async def stream_completion_with_context(self,
                                             context: List[Dict[str, str]],
                                             model: str = "gpt-3.5-turbo",
                                             max_tokens: int = 1000,
                                             temperature: float = 0.7,
                                             **kwargs):
        """
        Генерирует ответ в потоковом режиме с учетом контекста.

        Args:
            context: Контекст диалога
            model: Модель
            max_tokens: Максимальное количество токенов
            temperature: Температура

        Yields:
            Куски ответа и данные о токенах/стоимости
        """
        full_response = ""
        prompt_tokens = self.count_tokens_for_messages(context, model)

        try:
            # Запрашиваем потоковый ответ
            stream = await self.client.chat.completions.create(
                model=model,
                messages=context,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )

            # Собираем ответ по кускам
            async for chunk in stream:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        yield {"text": content}

            # Подсчет токенов и стоимости по завершении
            completion_tokens = len(tiktoken.encoding_for_model(model).encode(full_response))
            total_tokens = prompt_tokens + completion_tokens

            tokens_data = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }

            cost = await self.calculate_cost(
                prompt_tokens,
                completion_tokens,
                model
            )

            yield {"tokens": tokens_data, "cost": cost}

        except Exception as e:
            yield {"error": True, "error_message": str(e)}
import httpx
import asyncio
import tiktoken
from typing import Dict, Any, List, Optional
import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy import select

from app.services.base_ai_service import BaseAIService
from app.core.settings import settings
from app.db.models import UsageStatisticsOrm, ModelOrm, ProviderOrm
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

            # Получаем стоимость из ответа API (если она не предоставляется непосредственно в ответе,
            # то она будет рассчитана в методе, который вызывает generate_completion)
            # Для некоторых API может потребоваться дополнительный запрос для получения стоимости

            return {
                "text": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "tokens": tokens_data,
                "from_cache": False
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

            return {
                "text": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "tokens": tokens_data,
                "from_cache": False
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

    async def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Метод оставлен для совместимости с базовым классом.
        В текущей реализации стоимость должна приходить из внешнего источника.

        Args:
            prompt_tokens: Количество токенов в запросе
            completion_tokens: Количество токенов в ответе
            model: Имя модели

        Returns:
            0.0 (стоимость должна приходить из ответа API или другого источника)
        """
        return 0.0

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
            cost: Стоимость запроса (получена из ответа API)
        """
        try:
            today = date.today()

            # Получаем ID провайдера и модели
            provider_query = select(ProviderOrm).filter(ProviderOrm.code == "openai")
            provider_result = await db.execute(provider_query)
            provider = provider_result.scalars().first()

            if not provider:
                print("Провайдер OpenAI не найден в базе данных")
                return

            model_query = select(ModelOrm).filter(
                ModelOrm.code == model,
                ModelOrm.provider_id == provider.id
            )
            model_result = await db.execute(model_query)
            model_obj = model_result.scalars().first()

            if not model_obj:
                print(f"Модель {model} не найдена в базе данных")
                return

            # Ищем или создаем запись статистики за сегодня
            query = select(UsageStatisticsOrm).filter(
                UsageStatisticsOrm.user_id == user_id,
                UsageStatisticsOrm.provider_id == provider.id,
                UsageStatisticsOrm.model_id == model_obj.id,
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
                    provider_id=provider.id,
                    model_id=model_obj.id,
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

            # Подсчет токенов по завершении
            completion_tokens = len(tiktoken.encoding_for_model(model).encode(full_response))
            total_tokens = prompt_tokens + completion_tokens

            tokens_data = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }

            # Стоимость должна приходить из другого источника
            yield {"tokens": tokens_data, "from_cache": False}

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

            # Подсчет токенов по завершении
            completion_tokens = len(tiktoken.encoding_for_model(model).encode(full_response))
            total_tokens = prompt_tokens + completion_tokens

            tokens_data = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }

            # Стоимость должна приходить из другого источника
            yield {"tokens": tokens_data, "from_cache": False}

        except Exception as e:
            yield {"error": True, "error_message": str(e)}

    async def sync_openai_models(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Получает список доступных моделей от OpenAI API и синхронизирует их с базой данных.

        Функция:
        1. Получает актуальный список моделей от API
        2. Добавляет новые модели, которых нет в БД
        3. Обновляет существующие модели
        4. Отключает модели, которые больше не возвращаются API

        Args:
            db: Асинхронная сессия базы данных

        Returns:
            Словарь с результатами синхронизации:
            {
                "new_models": [список новых моделей],
                "updated_models": [список обновленных моделей],
                "deactivated_models": [список отключенных моделей]
            }
        """
        from sqlalchemy import select
        from app.db.models import ProviderOrm, ModelOrm

        # Результаты синхронизации
        result = {
            "new_models": [],
            "updated_models": [],
            "deactivated_models": []
        }

        try:
            # Получаем ID провайдера OpenAI
            provider_query = select(ProviderOrm).filter(ProviderOrm.code == "openai")
            provider_result = await db.execute(provider_query)
            provider = provider_result.scalars().first()

            if not provider:
                return {
                    "error": True,
                    "error_message": "Провайдер OpenAI не найден в базе данных"
                }

            # Получаем список всех моделей провайдера из БД
            models_query = select(ModelOrm).filter(ModelOrm.provider_id == provider.id)
            models_result = await db.execute(models_query)
            db_models = {model.code: model for model in models_result.scalars().all()}

            # Получаем актуальный список моделей от OpenAI API
            api_models_response = await self.client.models.list()

            # Обработка ответа от API
            # Проверяем, что ответ содержит список моделей в поле 'data'
            if hasattr(api_models_response, 'data'):
                api_models = api_models_response.data
            else:
                # Если 'data' отсутствует, возможно мы получили уже списк моделей
                api_models = api_models_response

            # Список кодов актуальных моделей для последующего отключения устаревших
            active_model_codes = set()

            # Отключаем автоматические события SQLAlchemy
            # Это предотвратит вызов кода, который пытается выполнить необработанный SQL
            from sqlalchemy import event
            from app.db.models import model_after_save

            # Временно отключаем обработчик событий
            event.remove(ModelOrm, 'after_insert', model_after_save)
            event.remove(ModelOrm, 'after_update', model_after_save)

            # Обрабатываем каждую модель из ответа API
            for api_model in api_models:
                # В зависимости от формата ответа API получаем id модели
                if hasattr(api_model, 'id'):
                    model_id = api_model.id
                elif isinstance(api_model, dict) and 'id' in api_model:
                    model_id = api_model['id']
                else:
                    # Если не можем получить id, пропускаем эту модель
                    continue

                active_model_codes.add(model_id)

                # Базовая информация о модели
                model_info = {
                    "code": model_id,
                    "name": model_id,  # В API нет отдельного поля для имени, используем id
                    "description": f"OpenAI модель {model_id}",
                    "is_active": True,
                    "supports_streaming": True,  # Большинство современных моделей поддерживают стриминг
                    "max_context_length": 4096,  # Значение по умолчанию
                    "input_price": 0.0,  # Значение по умолчанию
                    "output_price": 0.0,  # Значение по умолчанию
                }

                # Если модель уже существует в БД, обновляем её
                if model_id in db_models:
                    db_model = db_models[model_id]

                    # Проверяем, нужно ли обновлять модель
                    need_update = False
                    for key, value in model_info.items():
                        if hasattr(db_model, key) and getattr(db_model, key) != value:
                            setattr(db_model, key, value)
                            need_update = True

                    if need_update:
                        result["updated_models"].append(model_id)
                else:
                    # Создаем новую модель
                    new_model = ModelOrm(
                        provider_id=provider.id,
                        **model_info
                    )
                    db.add(new_model)
                    result["new_models"].append(model_id)

            # Отключаем модели, которых нет в ответе API
            for db_model_code, db_model in db_models.items():
                if db_model_code not in active_model_codes and db_model.is_active:
                    db_model.is_active = False
                    result["deactivated_models"].append(db_model_code)

            # Сохраняем изменения в БД
            await db.commit()

            # Восстанавливаем обработчики событий
            event.listen(ModelOrm, 'after_insert', model_after_save)
            event.listen(ModelOrm, 'after_update', model_after_save)

            return result

        except Exception as e:
            await db.rollback()
            # Попытка восстановить обработчики событий в случае ошибки
            try:
                from sqlalchemy import event
                from app.db.models import model_after_save
                event.listen(ModelOrm, 'after_insert', model_after_save)
                event.listen(ModelOrm, 'after_update', model_after_save)
            except:
                pass

            return {
                "error": True,
                "error_message": f"Ошибка при синхронизации моделей OpenAI: {str(e)}",
                "error_type": type(e).__name__
            }
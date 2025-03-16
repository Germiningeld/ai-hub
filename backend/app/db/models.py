from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Date, event, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy.sql import func
import re
import importlib
from typing import Optional, Type, Dict, Any

from app.db.database import Base


class ProviderEnum(str, Enum):
    """Перечисление поддерживаемых провайдеров"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    # Добавьте другие провайдеры по необходимости


class RoleEnum(str, Enum):
    """Перечисление ролей в диалоге"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ProviderOrm(Base):
    """Модель провайдера AI API"""
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # openai, anthropic, etc.
    name = Column(String(100), nullable=False)  # Полное название (OpenAI, Anthropic)
    description = Column(Text)
    is_active = Column(Boolean, default=True)  # Включен ли провайдер
    service_class = Column(String(100), nullable=False)  # Имя класса сервиса, например "OpenAIService"
    config = Column(JSON, default=lambda: {})  # Дополнительные параметры конфигурации провайдера
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    api_keys = relationship("ApiKeyOrm", back_populates="provider", lazy="dynamic")
    usage_statistics = relationship("UsageStatisticsOrm", back_populates="provider_obj", lazy="dynamic")
    threads = relationship("ThreadOrm", back_populates="provider_obj", lazy="dynamic")
    messages = relationship("MessageOrm", back_populates="provider_obj", lazy="dynamic")
    model_preferences = relationship("ModelPreferencesOrm", back_populates="provider_obj", lazy="dynamic")

    # Модели, поддерживаемые этим провайдером
    models = relationship("ModelOrm", back_populates="provider", cascade="all, delete-orphan", lazy="selectin")

    def get_service_class(self):
        """Динамически загружает класс сервиса из строкового имени"""
        try:
            # Если service_class включает полный путь
            if "." in self.service_class:
                module_path, class_name = self.service_class.rsplit(".", 1)
                module = importlib.import_module(module_path)
                return getattr(module, class_name)
            else:
                # Иначе предполагаем, что класс находится в стандартном пути
                module_path = f"app.services.{self.code}_service"
                module = importlib.import_module(module_path)
                return getattr(module, self.service_class)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Не удалось загрузить класс сервиса {self.service_class}: {str(e)}")

    def is_provider_active(self) -> bool:
        """Проверяет, активен ли провайдер и есть ли у него активные модели"""
        if not self.is_active:
            return False
        return any(model.is_active for model in self.models)

    @validates('code')
    def validate_code(self, key, code):
        """Валидация кода провайдера"""
        if code not in [e.value for e in ProviderEnum]:
            raise ValueError(f"Неизвестный код провайдера: {code}")
        return code.lower()  # Нормализуем код к нижнему регистру


class ModelOrm(Base):
    """Модель для моделей AI (GPT-4, Claude-3 и т.д.)"""
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)  # gpt-4, claude-3-opus, etc.
    name = Column(String(100), nullable=False)  # Полное название модели
    description = Column(Text)
    is_active = Column(Boolean, default=True)  # Доступна ли модель
    max_context_length = Column(Integer, default=4096)  # Максимальная длина контекста в токенах
    supports_streaming = Column(Boolean, default=True)  # Поддерживает ли потоковую генерацию
    input_price = Column(Float, default=0.0)  # Стоимость за 1K входных токенов
    output_price = Column(Float, default=0.0)  # Стоимость за 1K выходных токенов
    config = Column(JSON, default=lambda: {})  # Дополнительные параметры
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    provider = relationship("ProviderOrm", back_populates="models")
    usage_statistics = relationship("UsageStatisticsOrm", back_populates="model_obj", lazy="dynamic")
    threads = relationship("ThreadOrm", back_populates="model_obj", lazy="dynamic")
    messages = relationship("MessageOrm", back_populates="model_obj", lazy="dynamic")
    model_preferences = relationship("ModelPreferencesOrm", back_populates="model_obj", lazy="dynamic")

    @classmethod
    async def get_by_code(cls, session, code, provider_id=None):
        """
        Получает модель по её коду, опционально в рамках конкретного провайдера.

        Args:
            session: Сессия базы данных
            code: Код модели (например, 'gpt-4', 'claude-3-opus')
            provider_id: ID провайдера (опционально)

        Returns:
            Объект модели или None, если не найдена
        """
        query = select(cls).filter(cls.code == code)

        if provider_id:
            query = query.filter(cls.provider_id == provider_id)

        result = await session.execute(query)
        return result.scalars().first()

    def validate_parameters(self, max_tokens: int = None, temperature: float = None) -> Dict[str, Any]:
        """
        Проверяет, что параметры находятся в допустимых пределах для модели.

        Args:
            max_tokens: Максимальное количество токенов
            temperature: Температура (случайность) ответа

        Returns:
            Словарь с результатами валидации: {'is_valid': bool, 'errors': [str, ...]}
        """
        errors = []

        if max_tokens is not None and max_tokens > self.max_context_length:
            errors.append(
                f"max_tokens ({max_tokens}) превышает максимальную длину контекста модели ({self.max_context_length})"
            )

        if temperature is not None and not (0 <= temperature <= 1):
            errors.append(f"temperature ({temperature}) должна быть в диапазоне [0, 1]")

        additional_validations = self.config.get("validations", {})
        for param, rules in additional_validations.items():
            # Дополнительная валидация из config
            pass

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    @validates('code')
    def validate_model_code(self, key, code):
        """Проверяет, что код модели соответствует провайдеру"""
        if hasattr(self, 'provider') and self.provider is not None:
            provider_code = self.provider.code
            # Проверка на соответствие кода модели провайдеру
            # Например, модели OpenAI обычно начинаются с "gpt-"
            if provider_code == "openai" and not (
                    code.startswith("gpt-") or code.startswith("text-") or code.startswith("dall-")):
                raise ValueError(f"Код модели '{code}' не соответствует провайдеру OpenAI")
            # Модели Anthropic обычно начинаются с "claude-"
            elif provider_code == "anthropic" and not code.startswith("claude-"):
                raise ValueError(f"Код модели '{code}' не соответствует провайдеру Anthropic")
        return code


class UserOrm(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    preferences = Column(JSONB, default=lambda: {})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    api_keys = relationship("ApiKeyOrm", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    usage_statistics = relationship("UsageStatisticsOrm", back_populates="user", cascade="all, delete-orphan",
                                    lazy="dynamic")
    threads = relationship("ThreadOrm", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    thread_categories = relationship("ThreadCategoryOrm", back_populates="user", cascade="all, delete-orphan",
                                     lazy="selectin")
    saved_prompts = relationship("SavedPromptOrm", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    model_preferences = relationship("ModelPreferencesOrm", back_populates="user", cascade="all, delete-orphan",
                                     lazy="selectin")

    @validates('email')
    def validate_email(self, key, email):
        """Валидация email адреса"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Неверный формат email")
        return email


class ApiKeyOrm(Base):
    """Модель для API ключей различных провайдеров"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    api_key = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    user = relationship("UserOrm", back_populates="api_keys")
    provider = relationship("ProviderOrm", back_populates="api_keys")

    @staticmethod
    def detect_provider(api_key: str) -> Optional[str]:
        """Определяет провайдера по формату API ключа"""
        if not api_key:
            return None

        # OpenAI API ключи обычно начинаются с "sk-" и длиннее
        if api_key.startswith("sk-") and len(api_key) > 50:
            return "openai"

        # Anthropic API ключи имеют особый формат
        if api_key.startswith("sk-ant-"):
            return "anthropic"

        # Google API ключи часто имеют другой формат
        if api_key.startswith("AIza"):
            return "google"

        # Mistral AI ключи
        if api_key.startswith("mis-"):
            return "mistral"

        # Если не удалось определить по формату
        return None

    @validates('provider_id')
    def sync_provider_code(self, key, provider_id):
        """Синхронизирует provider_code при изменении provider_id"""
        session = Session.object_session(self)
        if session:
            provider = session.get(ProviderOrm, provider_id)
            if provider:
                self.provider_code = provider.code
        return provider_id

    @validates('provider_code')
    def validate_provider_code(self, key, provider_code):
        """Валидация кода провайдера"""
        if provider_code not in [e.value for e in ProviderEnum]:
            raise ValueError(f"Неподдерживаемый провайдер: {provider_code}")
        return provider_code


class UsageStatisticsOrm(Base):
    """Модель для статистики использования API"""
    __tablename__ = "usage_statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=False, index=True)
    request_date = Column(Date, nullable=False, index=True)
    request_count = Column(Integer, default=0)
    tokens_prompt = Column(Integer, default=0)
    tokens_completion = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    user = relationship("UserOrm", back_populates="usage_statistics")
    provider_obj = relationship("ProviderOrm", back_populates="usage_statistics")
    model_obj = relationship("ModelOrm", back_populates="usage_statistics")

    @validates('provider_id')
    def sync_provider_code(self, key, provider_id):
        """Синхронизирует provider_code при изменении provider_id"""
        session = Session.object_session(self)
        if session:
            provider = session.get(ProviderOrm, provider_id)
            if provider:
                self.provider_code = provider.code
        return provider_id

    @validates('model_id')
    def sync_model_code(self, key, model_id):
        """Синхронизирует model_code при изменении model_id"""
        session = Session.object_session(self)
        if session:
            model = session.get(ModelOrm, model_id)
            if model:
                self.model_code = model.code
        return model_id


class ThreadCategoryOrm(Base):
    """Модель для категорий тредов"""
    __tablename__ = "thread_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(20))  # Для цветовой метки в UI
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    user = relationship("UserOrm", back_populates="thread_categories")
    threads = relationship("ThreadOrm", back_populates="category", lazy="dynamic")
    saved_prompts = relationship("SavedPromptOrm", back_populates="category", lazy="dynamic")


class ThreadOrm(Base):
    """Модель для тредов (цепочек сообщений)"""
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("thread_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    thread_external_id = Column(String(255), nullable=True)  # ID треда во внешней системе

    # Отношения
    user = relationship("UserOrm", back_populates="threads")
    category = relationship("ThreadCategoryOrm", back_populates="threads")
    messages = relationship("MessageOrm", back_populates="thread", cascade="all, delete-orphan", lazy="dynamic",
                           order_by="MessageOrm.created_at")
    provider_obj = relationship("ProviderOrm", back_populates="threads")
    model_obj = relationship("ModelOrm", back_populates="threads")

    @validates('provider_id')
    def sync_provider_code(self, key, provider_id):
        """Синхронизирует provider_code при изменении provider_id"""
        session = Session.object_session(self)
        if session:
            provider = session.get(ProviderOrm, provider_id)
            if provider:
                self.provider_code = provider.code
        return provider_id

    @validates('model_id')
    def sync_model_code(self, key, model_id):
        """Синхронизирует model_code при изменении model_id"""
        session = Session.object_session(self)
        if session:
            model = session.get(ModelOrm, model_id)
            if model:
                self.model_code = model.code
        return model_id


class MessageOrm(Base):
    """Модель для сообщений в тредах"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)  # user, assistant, system
    content = Column(Text, nullable=False)
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    tokens_total = Column(Integer, default=0)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=True, index=True)
    provider_code = Column(String(50), nullable=True, index=True)  # Оставлено для обратной совместимости
    model_id = Column(Integer, ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=True, index=True)
    model_code = Column(String(50), nullable=True, index=True)  # Оставлено для обратной совместимости
    cost = Column(Float, default=0.0)
    is_cached = Column(Boolean, default=False)
    model_preference_id = Column(Integer, ForeignKey("model_preferences.id", ondelete="SET NULL"), nullable=True)
    meta_data = Column(JSON, default=lambda: {})  # Дополнительные метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    thread = relationship("ThreadOrm", back_populates="messages")
    provider_obj = relationship("ProviderOrm", back_populates="messages")
    model_obj = relationship("ModelOrm", back_populates="messages")
    model_preference = relationship("ModelPreferencesOrm")

    @validates('role')
    def validate_role(self, key, role):
        """Валидация роли по перечислению"""
        if role not in [e.value for e in RoleEnum]:
            raise ValueError(f"Неподдерживаемая роль: {role}")
        return role

    @validates('provider_id')
    def sync_provider_code(self, key, provider_id):
        """Синхронизирует provider_code при изменении provider_id"""
        if provider_id is not None:
            session = Session.object_session(self)
            if session:
                provider = session.get(ProviderOrm, provider_id)
                if provider:
                    self.provider_code = provider.code
        return provider_id

    @validates('model_id')
    def sync_model_code(self, key, model_id):
        """Синхронизирует model_code при изменении model_id"""
        if model_id is not None:
            session = Session.object_session(self)
            if session:
                model = session.get(ModelOrm, model_id)
                if model:
                    self.model_code = model.code
        return model_id


class SavedPromptOrm(Base):
    """Модель для сохраненных промптов"""
    __tablename__ = "saved_prompts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("thread_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    user = relationship("UserOrm", back_populates="saved_prompts")
    category = relationship("ThreadCategoryOrm", back_populates="saved_prompts")


class ModelPreferencesOrm(Base):
    """Модель для предпочтительных настроек моделей"""
    __tablename__ = "model_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=False, index=True)
    max_tokens = Column(Integer, default=1000)
    temperature = Column(Float, default=0.7)
    system_prompt = Column(Text)
    is_default = Column(Boolean, default=False)
    use_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    user = relationship("UserOrm", back_populates="model_preferences")
    provider_obj = relationship("ProviderOrm", back_populates="model_preferences")
    model_obj = relationship("ModelOrm", back_populates="model_preferences")

    @validates('provider_id')
    def sync_provider_code(self, key, provider_id):
        """Синхронизирует provider_code при изменении provider_id"""
        session = Session.object_session(self)
        if session:
            provider = session.get(ProviderOrm, provider_id)
            if provider:
                self.provider_code = provider.code
        return provider_id

    @validates('model_id')
    def sync_model_code(self, key, model_id):
        """Синхронизирует model_code при изменении model_id"""
        session = Session.object_session(self)
        if session:
            model = session.get(ModelOrm, model_id)
            if model:
                self.model_code = model.code
        return model_id

    @validates('temperature')
    def validate_temperature(self, key, temperature):
        """Валидация значения температуры"""
        if not 0 <= temperature <= 1:
            raise ValueError("Температура должна быть между 0 и 1")
        return temperature

    def validate_with_model(self):
        """Проверяет, что настройки соответствуют ограничениям модели"""
        if self.model_obj:
            result = self.model_obj.validate_parameters(
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return result
        return {"is_valid": False, "errors": ["Модель не найдена"]}


# События SQLAlchemy для автоматического обновления полей
@event.listens_for(ModelOrm, 'after_insert')
@event.listens_for(ModelOrm, 'after_update')
def model_after_save(mapper, connection, target):
    """Обновляет записи, ссылающиеся на данную модель"""
    # Этот код выполняется непосредственно на уровне соединения,
    # поэтому мы используем SQL запросы напрямую

    # Обновляем model_code в зависимых таблицах
    tables = ['threads', 'messages', 'usage_statistics', 'model_preferences']
    for table in tables:
        connection.execute(
            f"""
            UPDATE {table}
            SET model_code = :model_code
            WHERE model_id = :model_id
            """,
            {"model_code": target.code, "model_id": target.id}
        )


@event.listens_for(ProviderOrm, 'after_insert')
@event.listens_for(ProviderOrm, 'after_update')
def provider_after_save(mapper, connection, target):
    """Обновляет записи, ссылающиеся на данного провайдера"""
    # Обновляем provider_code в зависимых таблицах
    tables = ['api_keys', 'threads', 'messages', 'usage_statistics', 'model_preferences']
    for table in tables:
        connection.execute(
            f"""
            UPDATE {table}
            SET provider_code = :provider_code
            WHERE provider_id = :provider_id
            """,
            {"provider_code": target.code, "provider_id": target.id}
        )
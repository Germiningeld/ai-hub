from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

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
    preferences = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    api_keys = relationship("ApiKeyOrm", back_populates="user", cascade="all, delete-orphan")
    usage_statistics = relationship("UsageStatisticsOrm", back_populates="user", cascade="all, delete-orphan")


class ApiKeyOrm(Base):
    """Модель для API ключей различных провайдеров"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    api_key = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    user = relationship("UserOrm", back_populates="api_keys")


class UsageStatisticsOrm(Base):
    """Модель для статистики использования API"""
    __tablename__ = "usage_statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False, index=True)
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
    user = relationship("UserOrm")
    threads = relationship("ThreadOrm", back_populates="category")


class ThreadOrm(Base):
    """Модель для тредов (цепочек сообщений)"""
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("thread_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic, и т.д.
    model = Column(String(50), nullable=False)  # gpt-4, claude-3, и т.д.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    thread_external_id = Column(String(255), nullable=True)  # или другой подходящий тип

    # Отношения
    user = relationship("UserOrm")
    category = relationship("ThreadCategoryOrm", back_populates="threads")
    messages = relationship("MessageOrm", back_populates="thread", cascade="all, delete-orphan")


class MessageOrm(Base):
    """Модель для сообщений в тредах"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    tokens = Column(Integer, default=0)
    model = Column(String(50))  # Модель, которая использовалась для сообщения
    provider = Column(String(50))  # Провайдер модели
    meta_data = Column(JSON, default={})  # Дополнительные метаданные (время генерации, ошибки и т.д.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    thread = relationship("ThreadOrm", back_populates="messages")


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
    user = relationship("UserOrm")
    category = relationship("ThreadCategoryOrm")


class ModelPreferencesOrm(Base):
    """Модель для предпочтительных настроек моделей"""
    __tablename__ = "model_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    max_tokens = Column(Integer, default=1000)
    temperature = Column(Float, default=0.7)
    system_prompt = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Отношения
    user = relationship("UserOrm")
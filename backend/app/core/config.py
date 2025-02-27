import os
import secrets
from typing import List
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения
    """
    # Основные настройки приложения
    APP_ENV: str = "development"
    APP_NAME: str = "AIHub"
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_ROOT_PATH: str = ""

    # CORS настройки
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Настройки базы данных
    DATABASE_URL: PostgresDsn = "postgresql://postgres:postgres@localhost:5432/aihub"

    # Настройки безопасности
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Данные администратора по умолчанию
    DEFAULT_ADMIN_EMAIL: str = "admin@example.com"
    DEFAULT_ADMIN_PASSWORD: str = "AdminPassword123"
    DEFAULT_ADMIN_USERNAME: str = "admin"

    # Настройки безопасности
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создаем глобальный экземпляр настроек
settings = Settings()
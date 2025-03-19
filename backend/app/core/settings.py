import os
import secrets
from typing import List
from functools import lru_cache
from pydantic import field_validator
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
    APP_PORT: int = 4000
    APP_ROOT_PATH: str = ""

    # CORS настройки
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"

    @field_validator('ALLOWED_ORIGINS')
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # Настройки базы данных
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRESQL_ASYNCPG_URL: str
    DATABASE_URL: str


    # Настройки безопасности
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней

    # Данные администратора по умолчанию
    # DEFAULT_ADMIN_EMAIL: str
    # DEFAULT_ADMIN_PASSWORD: str
    # DEFAULT_ADMIN_USERNAME: str

    @property
    def DATABASE_ASYNCPG(self) -> str:
        return f"{self.POSTGRESQL_ASYNCPG_URL}"

    @property
    def DATABASE(self) -> str:
        return f"{self.DATABASE_URL}"

    @property
    def ORIGINS(self) -> List[str]:
        """Возвращает список разрешенных источников для CORS"""
        return self.ALLOWED_ORIGINS if isinstance(self.ALLOWED_ORIGINS, list) else \
            [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',') if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Создаем глобальный экземпляр настроек
settings = Settings()
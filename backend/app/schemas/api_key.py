from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ApiKeyBase(BaseModel):
    """Базовая схема для API ключа"""
    provider: str = Field(..., description="Провайдер API (openai, anthropic)")
    name: Optional[str] = Field(None, description="Понятное имя для ключа")
    is_active: bool = Field(True, description="Активен ли ключ")


class ApiKeyCreate(ApiKeyBase):
    """Схема для создания API ключа"""
    api_key: str = Field(..., description="Значение API ключа")


class ApiKeyUpdate(BaseModel):
    """Схема для обновления API ключа"""
    name: Optional[str] = Field(None, description="Понятное имя для ключа")
    api_key: Optional[str] = Field(None, description="Новое значение API ключа")
    is_active: Optional[bool] = Field(None, description="Активен ли ключ")


class ApiKeyResponse(ApiKeyBase):
    """Схема для ответа с API ключом"""
    id: int
    user_id: int
    api_key: str = Field(..., description="API ключ (в целях безопасности в ответе можно показывать только часть)")
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

        @staticmethod
        def schema_extra(schema, model):
            # В документации Swagger ключ будет показан частично
            props = schema.get('properties', {})
            if 'api_key' in props:
                props['api_key']['format'] = 'password'
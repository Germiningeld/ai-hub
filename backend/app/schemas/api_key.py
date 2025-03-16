from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ApiKeyBaseSchema(BaseModel):
    """Базовая схема для API ключа"""
    provider: str = Field(..., description="Провайдер API (openai, anthropic)")
    name: Optional[str] = Field(None, description="Понятное имя для ключа")
    is_active: bool = Field(True, description="Активен ли ключ")


class ApiKeyCreateSchema(ApiKeyBaseSchema):
    """Схема для создания API ключа"""
    api_key: str = Field(..., description="Значение API ключа")


class ApiKeyUpdateSchema(BaseModel):
    """Схема для обновления API ключа"""
    name: Optional[str] = Field(None, description="Понятное имя для ключа")
    api_key: Optional[str] = Field(None, description="Новое значение API ключа")
    is_active: Optional[bool] = Field(None, description="Активен ли ключ")


class ApiKeyResponseSchema(ApiKeyBaseSchema):
    """Схема для ответа с API ключом"""
    id: int
    user_id: int
    api_key: str = Field(..., description="API ключ (в целях безопасности в ответе показывается только часть)")
    created_at: datetime
    updated_at: datetime

    @validator('api_key')
    def mask_api_key(cls, v):
        # Если ключ меньше 16 символов, просто маскируем середину
        if len(v) <= 16:
            # Показываем максимум то, что можем (до 8 символов с каждой стороны)
            visible_chars = len(v) // 2
            return v[:visible_chars] + "****" + v[-visible_chars:]
        # Если длина достаточная, показываем первые и последние 8 символов
        return v[:8] + "****" + v[-8:]

    class Config:
        from_attributes = True

        @staticmethod
        def json_schema_extra(schema, model):
            props = schema.get('properties', {})
            if 'api_key' in props:
                props['api_key']['format'] = 'password'
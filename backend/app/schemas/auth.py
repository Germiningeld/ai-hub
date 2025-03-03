from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class TokenSchema(BaseModel):
    """Схема для ответа с токеном"""
    access_token: str
    token_type: str


class TokenPayloadSchema(BaseModel):
    """Схема для полезной нагрузки токена"""
    sub: Optional[int] = None
    exp: Optional[int] = None


class LoginSchema(BaseModel):
    """Схема для запроса логина"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strong_password"
            }
        }
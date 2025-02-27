from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Схема для ответа с токеном"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Схема для полезной нагрузки токена"""
    sub: Optional[int] = None
    exp: Optional[int] = None


class Login(BaseModel):
    """Схема для запроса логина"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strong_password"
            }
        }
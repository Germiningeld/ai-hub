from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема для пользователя"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    email: EmailStr
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strong_password"
            }
        }


class UserUpdate(UserBase):
    """Схема для обновления пользователя"""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Базовая схема для пользователя из БД"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """Схема для ответа с пользователем"""
    pass


class UserInDB(UserInDBBase):
    """Схема для пользователя в БД (содержит хеш пароля)"""
    password_hash: str
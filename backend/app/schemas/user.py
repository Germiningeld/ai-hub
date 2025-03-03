from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBaseSchema(BaseModel):
    """Базовая схема для пользователя"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreateSchema(UserBaseSchema):
    """Схема для создания пользователя"""
    email: EmailStr
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strong_password"
            }
        }


class UserUpdateSchema(UserBaseSchema):
    """Схема для обновления пользователя"""
    password: Optional[str] = None


class UserInDBBaseSchema(UserBaseSchema):
    """Базовая схема для пользователя из БД"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserSchema(UserInDBBaseSchema):
    """Схема для ответа с пользователем"""
    pass


class UserInDBSchema(UserInDBBaseSchema):
    """Схема для пользователя в БД (содержит хеш пароля)"""
    password_hash: str
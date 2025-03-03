from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from app.core.settings import settings

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли plaintext пароль хешу.

    Args:
        plain_password: Открытый пароль
        hashed_password: Хеш пароля из базы данных

    Returns:
        bool: True, если пароль соответствует хешу, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля для хранения в базе данных.

    Args:
        password: Пароль для хеширования

    Returns:
        str: Хеш пароля
    """
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен для аутентификации.

    Args:
        subject: Идентификатор пользователя (обычно id пользователя)
        expires_delta: Срок действия токена

    Returns:
        str: JWT токен
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt
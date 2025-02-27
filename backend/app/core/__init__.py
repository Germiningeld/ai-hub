"""
Ядро приложения AIHub.

Этот пакет содержит основные компоненты, необходимые для работы приложения,
включая настройки конфигурации, функции безопасности и общие зависимости.
"""

from app.core.config import settings
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token
)
from app.core.dependencies import get_current_user

__all__ = [
    "settings",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "get_current_user",
]
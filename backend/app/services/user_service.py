from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserOrm
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreateSchema, UserUpdateSchema


async def get_by_email(db: AsyncSession, email: str) -> Optional[UserOrm]:
    """
    Получает пользователя по email.

    Args:
        db: Сессия базы данных
        email: Email пользователя

    Returns:
        Optional[UserOrm]: Пользователь или None, если не найден
    """
    result = await db.execute(select(UserOrm).filter(UserOrm.email == email))
    return result.scalars().first()


async def get_by_username(db: AsyncSession, username: str) -> Optional[UserOrm]:
    """
    Получает пользователя по имени пользователя.

    Args:
        db: Сессия базы данных
        username: Имя пользователя

    Returns:
        Optional[UserOrm]: Пользователь или None, если не найден
    """
    result = await db.execute(select(UserOrm).filter(UserOrm.username == username))
    return result.scalars().first()


async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[UserOrm]:
    """
    Аутентифицирует пользователя по email и паролю.

    Args:
        db: Сессия базы данных
        email: Email пользователя
        password: Пароль пользователя

    Returns:
        Optional[UserOrm]: Пользователь, если аутентификация успешна, иначе None
    """
    user = await get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def create_user(db: AsyncSession, user_in: UserCreateSchema) -> UserOrm:
    """
    Создает нового пользователя.

    Args:
        db: Сессия базы данных
        user_in: Данные для создания пользователя

    Returns:
        UserOrm: Созданный пользователь
    """
    db_user = UserOrm(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdateSchema) -> Optional[UserOrm]:
    """
    Обновляет данные пользователя.

    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        user_in: Данные для обновления пользователя

    Returns:
        Optional[UserOrm]: Обновленный пользователь или None, если не найден
    """
    result = await db.execute(select(UserOrm).filter(UserOrm.id == user_id))
    user = result.scalars().first()

    if not user:
        return None

    update_data = user_in.dict(exclude_unset=True)

    if update_data.get("password"):
        password = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(password)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import User
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserUpdate


def get_by_email(db: Session, email: str) -> Optional[User]:
    """
    Получает пользователя по email.

    Args:
        db: Сессия базы данных
        email: Email пользователя

    Returns:
        Optional[User]: Пользователь или None, если не найден
    """
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> Optional[User]:
    """
    Получает пользователя по имени пользователя.

    Args:
        db: Сессия базы данных
        username: Имя пользователя

    Returns:
        Optional[User]: Пользователь или None, если не найден
    """
    return db.query(User).filter(User.username == username).first()


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    """
    Аутентифицирует пользователя по email и паролю.

    Args:
        db: Сессия базы данных
        email: Email пользователя
        password: Пароль пользователя

    Returns:
        Optional[User]: Пользователь, если аутентификация успешна, иначе None
    """
    user = get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Создает нового пользователя.

    Args:
        db: Сессия базы данных
        user_in: Данные для создания пользователя

    Returns:
        User: Созданный пользователь
    """
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """
    Обновляет данные пользователя.

    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        user_in: Данные для обновления пользователя

    Returns:
        Optional[User]: Обновленный пользователь или None, если не найден
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    update_data = user_in.dict(exclude_unset=True)

    if update_data.get("password"):
        password = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(password)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.settings import settings
from app.db.database import get_async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_async_session)
):
    """
    Получает текущего пользователя на основе JWT токена.
    """
    # Импортируем UserOrm здесь внутри функции, чтобы избежать циклического импорта
    from app.db.models import UserOrm

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Получаем пользователя из базы данных
    query = select(UserOrm).filter(UserOrm.id == user_id)
    result = await db.execute(query)
    user_tuple = result.first()

    if user_tuple is None:
        raise credentials_exception

    user = user_tuple[0]  # Получаем сам объект пользователя из кортежа

    if not user.is_active:
        raise credentials_exception

    return user

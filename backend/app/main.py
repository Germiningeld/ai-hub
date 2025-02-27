import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Исправляем импорты, добавляя префикс 'app'
from app.core.config import settings
from app.db.session import engine, get_db
from app.db.models import Base, User
from app.core.security import get_password_hash

# Создаем все таблицы в БД при запуске приложения
# В продакшене лучше использовать миграции через Alembic
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    root_path=settings.APP_ROOT_PATH,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем админа при первом запуске
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    # Проверяем, есть ли уже пользователь с таким email
    user = db.query(User).filter(User.email == settings.DEFAULT_ADMIN_EMAIL).first()
    if not user:
        # Создаем пользователя-админа
        new_user = User(
            username=settings.DEFAULT_ADMIN_USERNAME,
            email=settings.DEFAULT_ADMIN_EMAIL,
            password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            is_active=True,
            is_admin=True
        )
        db.add(new_user)
        db.commit()
        print(f"Создан администратор: {settings.DEFAULT_ADMIN_EMAIL}")


# Импортируем и регистрируем маршруты
# Подключаем маршруты API
from app.routers import api_keys, chats, auth, users
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["api-keys"])
app.include_router(chats.router, prefix="/api/chats", tags=["chats"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
import uvicorn
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

# Исправляем импорты
from app.core.settings import settings
from app.db.database import engine, Base, get_async_session
from app.db.models import UserOrm
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
    async for db in get_async_session():
        # Асинхронный запрос
        user = await db.execute(select(UserOrm).filter(UserOrm.email == settings.DEFAULT_ADMIN_EMAIL))
        user = user.scalars().first()
        if not user:
            # Создаем пользователя-админа
            new_user = UserOrm(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                is_active=True,
                is_admin=True
            )
            db.add(new_user)
            await db.commit()
            print(f"Создан администратор: {settings.DEFAULT_ADMIN_EMAIL}")


# Импортируем и регистрируем маршруты
from app.routers import api_keys, auth, users, threads, categories, prompts, model_preferences, statistics

# Аутентификация и пользователи
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

# API ключи
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["api-keys"])

# Чаты и треды
app.include_router(threads.router, prefix="/api/threads", tags=["threads"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])

# Промпты и настройки
app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])
app.include_router(model_preferences.router, prefix="/api/models", tags=["models"])

# Статистика
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
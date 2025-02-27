from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Создаем движок SQLAlchemy для подключения к PostgreSQL
engine = create_engine(str(settings.DATABASE_URL))

# Создаем фабрику сессий для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()


# Функция-зависимость для получения сессии БД
def get_db():
    """
    Функция-генератор, которая создает новую сессию для каждого запроса
    и закрывает ее после завершения запроса
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.settings import settings

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.DATABASE_ASYNCPG)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
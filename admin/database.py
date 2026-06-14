"""SQLAlchemy database setup"""
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from admin.config import DATABASE_URL

logger = logging.getLogger(__name__)


# Convert postgresql:// to postgresql+asyncpg:// for async
_engine_url = DATABASE_URL
if _engine_url.startswith("postgresql://"):
    _engine_url = _engine_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _engine_url.startswith("postgres://"):
    _engine_url = _engine_url.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(_engine_url, pool_size=10, max_overflow=20, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_models():
    """Create all tables defined in models."""
    async with engine.begin() as conn:
        from admin.models import admin_user, log, setting, broadcast, transaction
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Admin panel database tables created/verified")


async def dispose_engine():
    await engine.dispose()

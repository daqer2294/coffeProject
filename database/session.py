from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from config import settings
from database.base import Base


# =========================================================
# 🚀 ENGINE
# =========================================================

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # на этапе разработки полезно
)


# =========================================================
# 🗄 SESSION FACTORY
# =========================================================

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =========================================================
# 📦 INIT TABLES
# =========================================================

async def init_models() -> None:
    """
    Создание таблиц при первом запуске.
    Безопасно — существующие таблицы не трогает.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
import asyncio

from core.bot import bot
from core.dispatcher import dp

from database.session import engine
from database.base import Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    print("Bot starting...")

    # создаём таблицы при запуске
    await create_tables()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
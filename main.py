import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_settings
from bot.handlers import router


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = load_settings()
    bot = Bot(token=settings.tg_bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

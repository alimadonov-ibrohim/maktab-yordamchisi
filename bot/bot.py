import asyncio
import logging
import os
import sys

# Ensure backend/ (which contains the 'app' package) is importable
_backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from bot.handlers import start, parent, teacher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Bot cannot start.")
        return

    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(parent.router)
    dp.include_router(teacher.router)

    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

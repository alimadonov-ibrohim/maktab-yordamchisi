import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from app.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self):
        self._bot = None
        if settings.BOT_TOKEN:
            try:
                self._bot = Bot(token=settings.BOT_TOKEN)
            except Exception as e:
                logger.error(f"Failed to create bot: {e}")
                self._bot = None

    async def send_to_user(
        self,
        telegram_id: int,
        text: str,
        parse_mode: str = "HTML",
    ):
        if not self._bot or not telegram_id:
            return False
        try:
            await self._bot.send_message(
                chat_id=telegram_id,
                text=text,
                parse_mode=parse_mode,
            )
            return True
        except TelegramBadRequest as e:
            logger.warning(f"Telegram send error (message not logged): {type(e).__name__}")
            return False
        except Exception as e:
            logger.error(f"Telegram send error: {type(e).__name__}")
            return False

    async def notify_present(self, telegram_id: int, student_name: str, class_name: str, time_str: str):
        text = (
            "🟢 <b>Farzandingiz maktabga keldi</b>\n\n"
            f"{student_name}\n"
            f"{class_name} sinf\n\n"
            f"⏰ Vaqt: {time_str}"
        )
        return await self.send_to_user(telegram_id, text)

    async def notify_absent(self, telegram_id: int, student_name: str, class_name: str):
        text = (
            "🔴 <b>Farzandingiz bugun maktabga kelmadi.</b>\n\n"
            f"{student_name}\n"
            f"{class_name} sinf"
        )
        return await self.send_to_user(telegram_id, text)

    async def notify_late(self, telegram_id: int, student_name: str, class_name: str, time_str: str, late_minutes: int):
        text = (
            "🟠 <b>Farzandingiz maktabga kechikib keldi.</b>\n\n"
            f"{student_name}\n"
            f"{class_name} sinf\n\n"
            f"Kelish vaqti: {time_str}\n"
            f"⏰ {late_minutes} daqiqa kechikdi"
        )
        return await self.send_to_user(telegram_id, text)


notifier = TelegramNotifier()

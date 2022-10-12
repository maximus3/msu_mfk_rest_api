from app.bot_helper import bot
from app.config import get_settings


async def send_error_message(message: str) -> None:
    while len(message) > 4000:
        await bot.bot.send_message(
            get_settings().TG_ERROR_CHAT_ID,
            message[:4000],
        )
        message = message[4000:]

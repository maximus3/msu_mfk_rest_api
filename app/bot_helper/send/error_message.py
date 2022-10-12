from app.bot_helper import bot
from app.config import get_settings


async def send_error_message(message: str) -> None:
    while len(message) > 0:
        await bot.bot.send_message(
            chat_id=get_settings().TG_ERROR_CHAT_ID,
            text=message[:4000],
        )
        message = message[4000:]

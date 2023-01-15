from app.bot_helper import bot
from app.config import get_settings


async def send_or_edit(message: str, message_id: str | None = None) -> None:
    if message_id is None:
        message_id = await bot.bot.send_message(
            chat_id=get_settings().TG_ERROR_CHAT_ID,
            text=message,
            disable_notification=True,
        )
    else:
        await bot.bot.edit_message_text(
            chat_id=get_settings().TG_ERROR_CHAT_ID,
            message_id=message_id,
            text=message,
        )
    return message_id

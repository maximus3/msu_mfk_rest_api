from aiogram import types

from app.bot_helper import bot
from app.config import get_settings


async def send_results(filenames: list[str]) -> None:
    settings = get_settings()
    docs = types.MediaGroup()
    _ = [docs.attach_document(types.InputFile(f)) for f in filenames]
    await bot.bot.send_media_group(
        chat_id=settings.TG_DB_DUMP_CHAT_ID,
        media=docs,
        disable_notification=True,
    )

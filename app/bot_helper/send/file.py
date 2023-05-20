import pathlib

from aiogram.utils import exceptions as aiogram_exceptions

from app.bot_helper import bot
from app.config import get_settings


async def send_file(
    filename: str | pathlib.Path, caption: str, chat_id: str | None = None
) -> None:
    chat_id = chat_id or get_settings().TG_ERROR_CHAT_ID
    try:
        with open(filename, 'rb') as f:
            await bot.bot.send_document(
                chat_id=chat_id,
                document=f,
                caption=caption,
                disable_notification=True,
            )
    except aiogram_exceptions.NetworkError as exc:
        if str(exc).startswith('File too large for uploading'):
            with open(filename, 'rb') as f:
                await bot.bot_client.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=caption,
                    disable_notification=True,
                )
        else:
            raise exc

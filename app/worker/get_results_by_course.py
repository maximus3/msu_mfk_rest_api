import asyncio
import functools
import time

from app import config
from app.bot_helper import bot


def async_to_sync(func):  # type: ignore
    @functools.wraps(func)
    def wrapped(*args, **kwargs):  # type: ignore
        return asyncio.run(func(*args, **kwargs))

    return wrapped


@async_to_sync
async def task() -> bool:
    time.sleep(10)
    settings = config.get_settings()
    await bot.bot_students.send_message(
        chat_id=settings.TG_ERROR_CHAT_ID,
        text='From task',
    )
    return True

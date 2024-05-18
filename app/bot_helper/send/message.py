import typing as tp

import loguru
from aiogram.utils.exceptions import CantParseEntities

from app.bot_helper import bot
from app.config import get_settings


async def send_message(
    message: str, level: str = 'error', chat_id: str | None = None
) -> None:
    chat_id = chat_id or get_settings().TG_ERROR_CHAT_ID
    while len(message) > 0:
        try:
            await bot.bot.send_message(
                chat_id=chat_id,
                text=message[:4000],
                disable_notification=level != 'error',
                parse_mode='HTML',
            )
            message = message[4000:]
        except CantParseEntities as e:
            if (
                str(e) == "Can't parse entities: can't find end "
                'tag corresponding to start tag code'
            ):
                await bot.bot.send_message(
                    chat_id=chat_id,
                    text=message[:4000] + '</code>',
                    disable_notification=level != 'error',
                    parse_mode='HTML',
                )
                message = '<code>' + message[4000:]
            else:
                raise e


async def send_traceback_message(
    message: str, code: str, level: str = 'error'
) -> None:
    message = (
        f'{message.replace("<", "&lt;").replace(">", "&gt;")}\n\n'
        f'<code>'
        f'{code.replace("<", "&lt;").replace(">", "&gt;")}'
        f'</code>'
    )
    return await send_message(message, level)


async def send_message_safe(
    logger: 'loguru.Logger', *args: tp.Any, **kwargs: tp.Any
) -> None:
    try:
        await send_message(*args, **kwargs)
    except Exception as send_exc:  # pylint: disable=broad-except
        logger.exception('Error while sending error message: {}', send_exc)


async def send_traceback_message_safe(
    logger: 'loguru.Logger', *args: tp.Any, **kwargs: tp.Any
) -> None:
    try:
        await send_traceback_message(*args, **kwargs)
    except Exception as send_exc:  # pylint: disable=broad-except
        logger.exception('Error while sending error message: {}', send_exc)

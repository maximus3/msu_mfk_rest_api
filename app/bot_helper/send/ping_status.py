from datetime import datetime

from app.bot_helper.bot import bot
from app.config import get_settings


MESSAGE_ID = None


async def send_ping_status(result: dict[str, dict[str, str]]) -> None:
    all_ok = True
    message = (
        f'Ping status (last update: '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}):\n'
    )
    for host, endpoints in result.items():
        message += f'\n{host}:\n'
        for endpoint, status in endpoints.items():
            all_ok = all_ok and status == 'Successful'
            emoji = '✅' if status == 'Successful' else '❌'
            message += f'{emoji}{endpoint}: {status}\n'
    global MESSAGE_ID  # pylint: disable=global-statement
    if MESSAGE_ID is None or not all_ok:
        MESSAGE_ID = await bot.send_message(
            chat_id=get_settings().TG_ERROR_CHAT_ID,
            text=message,
        )
        await bot.pin_chat_message(
            chat_id=get_settings().TG_ERROR_CHAT_ID,
            message_id=MESSAGE_ID.message_id,
        )
    else:
        await bot.edit_message_text(
            chat_id=get_settings().TG_ERROR_CHAT_ID,
            message_id=MESSAGE_ID.message_id,
            text=message,
        )

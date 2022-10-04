from aiogram import Bot

from app.config import get_settings


bot = Bot(token=get_settings().TG_HELPER_BOT_TOKEN)


async def send_db_dump(filename: str) -> None:
    settings = get_settings()
    with open(filename, 'rb') as f:
        await bot.send_document(
            chat_id=get_settings().TG_DB_DUMP_CHAT_ID,
            document=f,
            caption=f'{settings.PROJECT_NAME}',
            disable_notification=True,
        )


async def send_error_message(message: str) -> None:
    await bot.send_message(
        chat_id=get_settings().TG_ERROR_CHAT_ID,
        text=message,
    )

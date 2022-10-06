from app.bot_helper.bot import bot
from app.config import get_settings


async def send_db_dump(filename: str) -> None:
    settings = get_settings()
    with open(filename, 'rb') as f:
        await bot.send_document(
            chat_id=get_settings().TG_DB_DUMP_CHAT_ID,
            document=f,
            caption=f'{settings.PROJECT_NAME}',
            disable_notification=True,
        )

from app.config import get_settings

from .file import send_file


async def send_db_dump(filename: str) -> None:
    settings = get_settings()
    return await send_file(
        filename, settings.PROJECT_NAME, chat_id=settings.TG_DB_DUMP_CHAT_ID
    )

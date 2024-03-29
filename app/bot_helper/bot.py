import aiogram
import pyrogram

from app.config import get_settings


_settings = get_settings()
bot = aiogram.Bot(token=_settings.TG_HELPER_BOT_TOKEN)
bot_client = pyrogram.Client(
    'tg_helper_app_account',
    _settings.TG_HELPER_APP_API_ID,
    _settings.TG_HELPER_APP_API_HASH,
    session_string=_settings.TG_HELPER_APP_SESSION_STRING,
)
bot_students = aiogram.Bot(token=_settings.TG_STUDENTS_BOT_TOKEN)

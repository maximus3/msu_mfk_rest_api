import aiogram
import loguru
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
try:
    bot_client.start()
except Exception:  # pylint: disable=broad-except
    loguru.logger.warning('Failed to start bot_client')

from aiogram import Bot

from app.config import get_settings


bot = Bot(token=get_settings().TG_HELPER_BOT_TOKEN)

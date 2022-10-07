import pytest
from aiogram import types

from app.bot_helper import send
from app.config import get_settings


pytestmark = pytest.mark.asyncio


class TestSendResultsHandler:
    async def test_send_results(self, tmp_files, mock_bot):
        settings = get_settings()
        await send.send_results(tmp_files)
        mock_bot.send_media_group.assert_called_once()
        assert (
            mock_bot.send_media_group.call_args[1]['chat_id']
            == settings.TG_DB_DUMP_CHAT_ID
        )
        assert mock_bot.send_media_group.call_args[1]['disable_notification']
        assert isinstance(
            mock_bot.send_media_group.call_args[1]['media'], types.MediaGroup
        )
        assert len(
            mock_bot.send_media_group.call_args[1]['media'].media
        ) == len(tmp_files)
        del mock_bot.send_media_group.call_args[1]['media'].media

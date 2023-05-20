from pathlib import Path
from unittest.mock import AsyncMock

import aiogram.utils.exceptions
import pytest

from app.bot_helper import send
from app.config import get_settings


pytestmark = pytest.mark.asyncio


class TestSendDbDumpHandler:
    async def test_send_db_dump(self, tmp_file, mock_bot):
        settings = get_settings()
        await send.send_db_dump(tmp_file)
        mock_bot.send_document.assert_called_once()
        assert Path(
            mock_bot.send_document.call_args[1]['document'].name
        ) == Path(tmp_file)
        assert (
            mock_bot.send_document.call_args[1]['chat_id']
            == settings.TG_DB_DUMP_CHAT_ID
        )
        assert (
            mock_bot.send_document.call_args[1]['caption']
            == settings.PROJECT_NAME
        )
        assert (
            mock_bot.send_document.call_args[1]['disable_notification'] is True
        )

    async def test_send_db_dump_big_file(
        self, tmp_file, mock_bot, mock_bot_client
    ):
        mock_bot.send_document = AsyncMock(
            side_effect=aiogram.utils.exceptions.NetworkError(
                'File too large for uploading'
            )
        )
        settings = get_settings()
        await send.send_db_dump(tmp_file)
        mock_bot.send_document.assert_called_once()
        mock_bot_client.send_document.assert_called_once()
        assert Path(
            mock_bot.send_document.call_args[1]['document'].name
        ) == Path(tmp_file)
        assert (
            mock_bot.send_document.call_args[1]['chat_id']
            == settings.TG_DB_DUMP_CHAT_ID
        )
        assert (
            mock_bot.send_document.call_args[1]['caption']
            == settings.PROJECT_NAME
        )
        assert (
            mock_bot.send_document.call_args[1]['disable_notification'] is True
        )

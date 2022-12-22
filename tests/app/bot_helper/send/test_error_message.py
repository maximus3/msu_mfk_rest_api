from unittest import mock

import pytest

from app.bot_helper import send
from app.config import get_settings


pytestmark = pytest.mark.asyncio


class TestSendErrorMessageHandler:
    async def test_send_message(self, mock_bot):
        settings = get_settings()
        await send.send_message('test')
        mock_bot.send_message.assert_called_once_with(
            chat_id=settings.TG_ERROR_CHAT_ID,
            text='test',
            disable_notification=False,
            parse_mode='HTML',
        )

    async def test_send_message_long(self, mock_bot):
        settings = get_settings()
        await send.send_message('t' * 5000)
        mock_bot.send_message.assert_has_calls(
            [
                mock.call(
                    chat_id=settings.TG_ERROR_CHAT_ID,
                    text='t' * 4000,
                    disable_notification=False,
                    parse_mode='HTML',
                ),
                mock.call(
                    chat_id=settings.TG_ERROR_CHAT_ID,
                    text='t' * 1000,
                    disable_notification=False,
                    parse_mode='HTML',
                ),
            ],
        )

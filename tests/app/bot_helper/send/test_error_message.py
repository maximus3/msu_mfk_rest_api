import pytest

from app.bot_helper import send
from app.config import get_settings


pytestmark = pytest.mark.asyncio


class TestSendErrorMessageHandler:
    async def test_send_error_message(self, mock_bot):
        settings = get_settings()
        await send.send_error_message('test')
        mock_bot.send_message.assert_called_once_with(
            chat_id=settings.TG_ERROR_CHAT_ID,
            text='test',
        )

import pytest

from app.bot_helper import send
from app.config import get_settings


pytestmark = pytest.mark.asyncio


class TestSendPingStatusHandler:
    async def test_send_ping_status_no_message(self, mock_bot):
        settings = get_settings()
        await send.send_ping_status(
            {
                'host1': {
                    'endpoint1': 'Successful',
                    'endpoint2': 'Successful',
                },
                'host2': {
                    'endpoint1': 'Successful',
                    'endpoint2': 'Successful',
                },
            }
        )
        mock_bot.send_message.assert_called_once()
        assert (
            mock_bot.send_message.call_args.kwargs['chat_id']
            == settings.TG_ERROR_CHAT_ID
        )
        mock_bot.pin_chat_message.assert_called_once_with(
            chat_id=settings.TG_ERROR_CHAT_ID,
            message_id=mock_bot.send_message.return_value.message_id,
        )
        mock_bot.edit_message_text.assert_not_called()

    async def test_send_ping_status_was_message(
        self, mock_bot, mock_message_id
    ):
        settings = get_settings()
        await send.send_ping_status(
            {
                'host1': {
                    'endpoint1': 'Successful',
                    'endpoint2': 'Successful',
                },
                'host2': {
                    'endpoint1': 'Successful',
                    'endpoint2': 'Successful',
                },
            }
        )
        mock_bot.send_message.assert_not_called()
        mock_bot.pin_chat_message.assert_not_called()
        mock_bot.edit_message_text.assert_called_once()
        assert (
            mock_bot.edit_message_text.call_args.kwargs['chat_id']
            == settings.TG_ERROR_CHAT_ID
        )
        assert (
            mock_bot.edit_message_text.call_args.kwargs['message_id']
            == mock_message_id.message_id
        )

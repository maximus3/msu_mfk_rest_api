from unittest.mock import AsyncMock

import pytest
from aiogram import Bot, types


@pytest.fixture(name='bot_token')
def bot_token_fixture():
    return (
        '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234'
    )


@pytest.fixture(name='bot')
async def bot_fixture(bot_token):
    """Bot fixture"""
    _bot = Bot(bot_token)
    _bot.send_document = AsyncMock()
    _bot.send_message = AsyncMock()
    _bot.send_message.return_value = types.Message(message_id=46456)
    _bot.send_media_group = AsyncMock()
    _bot.pin_chat_message = AsyncMock()
    _bot.edit_message_text = AsyncMock()
    yield _bot
    session = await _bot.get_session()
    await session.close()


@pytest.fixture
async def mock_bot(mocker, bot):
    """Mock bot fixture"""
    mock = mocker.patch('app.bot_helper.bot.bot', bot)
    return mock


@pytest.fixture
def mock_message_id(mocker):
    """Mock message id fixture"""
    mock = mocker.patch(
        'app.bot_helper.send.ping_status.MESSAGE_ID',
        types.Message(message_id=453534),
    )
    return mock

from unittest.mock import AsyncMock, Mock

import pytest
from aiogram import types


@pytest.fixture(name='bot')
async def bot_fixture():
    """Bot fixture"""
    _bot = Mock()
    _bot.send_document = AsyncMock()
    _bot.send_message = AsyncMock()
    _bot.send_message.return_value = types.Message(message_id=46456)
    _bot.send_media_group = AsyncMock()
    _bot.pin_chat_message = AsyncMock()
    _bot.edit_message_text = AsyncMock()
    yield _bot


@pytest.fixture(name='bot_client')
async def bot_client_fixture():
    """Bot client fixture"""
    _bot_client = Mock()
    _bot_client.send_document = AsyncMock()
    _bot_client.__aenter__ = AsyncMock()
    _bot_client.__aexit__ = AsyncMock()
    yield _bot_client


@pytest.fixture
async def mock_bot(mocker, bot):
    """Mock bot fixture"""
    mock = mocker.patch('app.bot_helper.bot.bot', bot)
    return mock


@pytest.fixture
async def mock_bot_client(mocker, bot_client):
    """Mock bot client fixture"""
    mock = mocker.patch('app.bot_helper.bot.bot_client', bot_client)
    return mock


@pytest.fixture
async def mock_send_or_edit(mocker):
    """Mock send_or_edit func"""
    mock = mocker.patch('app.bot_helper.send.send_or_edit')
    return mock


@pytest.fixture
def mock_message_id(mocker):
    """Mock message id fixture"""
    mock = mocker.patch(
        'app.bot_helper.send.ping_status.MESSAGE_ID',
        types.Message(message_id=453534),
    )
    return mock

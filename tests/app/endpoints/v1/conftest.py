from os import environ
from pathlib import Path
from uuid import uuid4

import pytest

from app.config import get_settings


@pytest.fixture(name='mock_logging_file')
def fixture_mock_logging_file():
    settings = get_settings()

    tmp_name = '.'.join([uuid4().hex, 'pytest'])
    settings.LOGGING_APP_FILE = Path(tmp_name)
    environ['LOGGING_APP_FILE'] = tmp_name

    yield tmp_name

    if Path(tmp_name).exists():
        Path(tmp_name).unlink()


@pytest.fixture
def mock_logging_file_exists(mock_logging_file):
    with open(mock_logging_file, 'w', encoding='utf-8') as f:
        f.write('{"test": "test"}')

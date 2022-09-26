from datetime import datetime

import pytest


@pytest.fixture
def datetime_utcnow_mock(mocker):
    """
    Mocks datetime.datetime.utcnow.
    """
    mock = mocker.patch('app.utils.user.service.datetime')
    mock.utcnow.return_value = datetime(2020, 1, 1, 0, 0, 0)

    mock_datetime = mocker.patch('datetime.datetime')
    mock_datetime.utcnow.return_value = datetime(2020, 1, 1, 0, 0, 0)


@pytest.fixture
def token_with_exp():
    return (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNTc3ODM2ODYwfQ.'
        'Ot5qkejyUwvLUObM3OT0z7X2VKhMBQzveKVZBn3RqKk'
    )


@pytest.fixture
def token_without_exp():
    return (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNTc3OTIzMjAwfQ.'
        'mj_K5rvnT6ljv4tMhctvRv7j82brv8cIZBCpTzAUVOQ'
    )

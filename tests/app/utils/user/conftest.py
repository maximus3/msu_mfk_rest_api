from datetime import datetime

import pytest


@pytest.fixture
def datetime_utcnow_mock(mocker):
    """
    Mocks datetime.datetime.utcnow.
    """
    mock = mocker.patch('app.utils.user.service.datetime')
    mock.utcnow.return_value = datetime(2020, 1, 1, 0, 0, 0)


@pytest.fixture
def token_with_exp():
    return (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNTc3ODM2ODYwfQ.'
        'dVy1nn6AS6u4UY4qx45DLnxeGpdBoJlQNP9BGsz0xXM'
    )


@pytest.fixture
def token_without_exp():
    return (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNTc3OTIzMjAwfQ.'
        'WUbpwI4pkMz46SiWdSUH4NLmN0UhCkq3MbNVB1XgJyI'
    )

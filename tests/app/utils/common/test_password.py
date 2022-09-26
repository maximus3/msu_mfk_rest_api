import pytest

from app.utils import common


pytestmark = pytest.mark.asyncio


class TestGetHostnameHandler:
    async def test_get_hostname_ok(self):
        assert common.hash_password('password') != 'password'

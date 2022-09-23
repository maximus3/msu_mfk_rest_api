import pytest

from app.utils import health_check


pytestmark = pytest.mark.asyncio


class TestHealthCheckDbHandler:
    async def test_health_check_db(self, session):
        assert await health_check.health_check_db(session)

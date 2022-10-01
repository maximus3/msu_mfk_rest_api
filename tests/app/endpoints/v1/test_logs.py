import pytest
from fastapi import status

from app.config import get_settings
from app.endpoints.v1 import prefix


pytestmark = pytest.mark.asyncio


class TestGetHandler:
    @staticmethod
    def get_url() -> str:
        settings = get_settings()
        return f'{settings.PATH_PREFIX}{prefix}/logs/app'

    async def test_get(self, client, user_headers):
        response = await client.get(url=self.get_url(), headers=user_headers)
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.text

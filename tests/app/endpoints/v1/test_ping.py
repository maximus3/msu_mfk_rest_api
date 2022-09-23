import pytest
from fastapi import status

from app.config import get_settings
from app.endpoints.v1 import prefix


pytestmark = pytest.mark.asyncio


class TestHealthCheckHandler:
    @staticmethod
    def get_url_application() -> str:
        settings = get_settings()
        return f'{settings.PATH_PREFIX}{prefix}/health_check/ping_application'

    @staticmethod
    def get_url_database() -> str:
        settings = get_settings()
        return f'{settings.PATH_PREFIX}{prefix}/health_check/ping_database'

    async def test_ping_application(self, client):
        response = await client.get(url=self.get_url_application())
        assert response.status_code == status.HTTP_200_OK, response.json()

    async def test_ping_database(self, client):
        response = await client.get(url=self.get_url_database())
        assert response.status_code == status.HTTP_200_OK, response.json()


class TestPingAuthHandler:
    @staticmethod
    def get_url_auth() -> str:
        settings = get_settings()
        return f'{settings.PATH_PREFIX}{prefix}/health_check/ping_auth'

    async def test_ping_auth(self, client, created_user, user_headers):
        response = await client.get(
            url=self.get_url_auth(), headers=user_headers
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json().get('detail')
        assert response.json()['detail'] == created_user.username

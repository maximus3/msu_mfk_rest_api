# pylint: disable=unused-argument

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

    async def test_get_no_exists(
        self, client, user_headers, mock_logging_file
    ):
        response = await client.get(url=self.get_url(), headers=user_headers)
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == {'items': [], 'count': 0}

    async def test_get(self, client, user_headers, mock_logging_file_exists):
        response = await client.get(url=self.get_url(), headers=user_headers)
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == {'count': 1, 'items': [{'test': 'test'}]}

    async def test_get_cp1252(self, client, user_headers, mock_logging_file):
        with open(mock_logging_file, 'w', encoding='cp1252') as f:
            f.write('{"test": "test"}')

        response = await client.get(url=self.get_url(), headers=user_headers)
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == {'count': 1, 'items': [{'test': 'test'}]}

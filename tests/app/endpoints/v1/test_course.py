import pytest
from fastapi import status

from app.config import get_settings
from app.endpoints.v1 import prefix
from app.schemas import CourseResponse


pytestmark = pytest.mark.asyncio


class TestGetHandler:
    @staticmethod
    def get_url() -> str:
        settings = get_settings()
        return f'{settings.PATH_PREFIX}{prefix}/course'

    async def test_get_no_exists(self, client, user_headers):
        response = await client.get(url=self.get_url(), headers=user_headers)
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == CourseResponse(items=[])

    async def test_get(self, client, user_headers, created_course):
        response = await client.get(url=self.get_url(), headers=user_headers)
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == CourseResponse(items=[created_course])

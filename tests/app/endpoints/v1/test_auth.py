# pylint: disable=unused-argument

import pytest
from fastapi import status

from app.config import get_settings
from app.endpoints.v1 import prefix
from app.utils import user


pytestmark = pytest.mark.asyncio


class BaseHandler:
    settings = get_settings()

    @classmethod
    def get_url(cls, path: str) -> str:
        return f'{cls.settings.PATH_PREFIX}{prefix}/user/{path}'


class TestAuthenticationHandler(BaseHandler):
    @staticmethod
    def get_data(username: str, password: str) -> dict[str, str]:
        return {'username': username, 'password': password}

    async def test_authentication_no_data(self, client):
        response = await client.post(url=self.get_url('authentication'))
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        ), response.json()

    async def test_authentication_no_user(self, client, potential_user):
        response = await client.post(
            url=self.get_url('authentication'),
            data=self.get_data(
                potential_user.username, potential_user.password
            ),
        )
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_authentication_wrong_password(
        self, client, created_user, potential_user
    ):
        response = await client.post(
            url=self.get_url('authentication'),
            data=self.get_data(potential_user.username, 'wrong_password'),
        )
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_authentication_success(
        self, client, created_user, potential_user
    ):
        response = await client.post(
            url=self.get_url('authentication'),
            data=self.get_data(
                potential_user.username, potential_user.password
            ),
        )
        assert response.status_code == status.HTTP_200_OK, response.json()


class TestGetMeHandler(BaseHandler):
    async def test_get_me_no_token(self, client):
        response = await client.get(url=self.get_url('me'))
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_get_me_bad_token(self, client):
        response = await client.get(
            url=self.get_url('me'),
            headers={'Authorization': 'Bearer wrong_token'},
        )
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_get_me_bad_token_no_username(self, client):
        response = await client.get(
            url=self.get_url('me'),
            headers={
                'Authorization': f'Bearer {user.create_access_token(data={})}'
            },
        )
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_get_me_bad_token_no_user(self, client, potential_user):
        token = user.create_access_token(data={'sub': potential_user.username})
        response = await client.get(
            url=self.get_url('me'),
            headers={'Authorization': f'Bearer {token}'},
        )
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_get_me_ok(self, client, created_user, user_headers):
        response = await client.get(
            url=self.get_url('me'), headers=user_headers
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()['username'] == created_user.username

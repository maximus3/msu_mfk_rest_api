# pylint: disable=unused-argument

from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import get_settings
from app.utils import user


pytestmark = pytest.mark.asyncio


class TestAuthenticateUserHandler:
    async def test_authenticate_user_no_username(
        self, session, potential_user
    ):
        assert not await user.authenticate_user(
            session, potential_user.username, potential_user.password
        )

    async def test_authenticate_user_wrong_password(
        self, session, created_user
    ):
        assert not await user.authenticate_user(
            session, created_user.username, 'wrong_password'
        )

    async def test_authenticate_user_ok(
        self, session, created_user, potential_user
    ):
        assert await user.authenticate_user(
            session, potential_user.username, potential_user.password
        )


class TestCreateAccessTokenHandler:
    @staticmethod
    def get_username(token: str) -> str:
        payload = jwt.decode(
            token,
            get_settings().SECRET_KEY,
            algorithms=[get_settings().ALGORITHM],
        )
        return payload.get('sub')

    async def test_create_access_token_with_expires_delta(self):
        access_token_expires = timedelta(minutes=1)
        token = user.create_access_token(
            data={'sub': 'test'}, expires_delta=access_token_expires
        )
        assert self.get_username(token) == 'test'

    async def test_create_access_token(self):
        token = user.create_access_token(data={'sub': 'test'})
        assert self.get_username(token) == 'test'


class TestVerifyPasswordHandler:
    async def test_verify_password_ok(self, not_created_user, potential_user):
        assert user.verify_password(
            potential_user.password, not_created_user.password
        )

    async def test_verify_password_wrong_password(self):
        settings = get_settings()
        hashed_wrong_password = settings.PWD_CONTEXT.hash('wrong_password')
        assert not user.verify_password('password', hashed_wrong_password)


@pytest.mark.usefixtures('migrated_postgres')
class TestGetCurrentUserHandler:
    async def test_get_current_user_no_token(self):
        with pytest.raises(HTTPException):
            await user.get_current_user('')

    async def test_get_current_user_username_none(self):
        with pytest.raises(HTTPException):
            await user.get_current_user(user.create_access_token(data={}))

    async def test_get_current_user_user_none(self, potential_user):
        with pytest.raises(HTTPException):
            await user.get_current_user(
                user.create_access_token(
                    data={'sub': potential_user.username}
                ),
            )

    async def test_get_current_user_ok(self, created_user):
        user_model = await user.get_current_user(
            user.create_access_token(data={'sub': created_user.username}),
        )
        assert user_model is not None
        assert user_model.id == created_user.id

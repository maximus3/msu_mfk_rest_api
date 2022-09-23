import pytest

from app.utils import user


pytestmark = pytest.mark.asyncio


class TestGetUserHandler:
    async def test_get_user_no_user(self, session, potential_user):
        assert (
            await user.get_user(
                session=session, username=potential_user.username
            )
            is None
        )

    async def test_get_user_ok(self, session, created_user):
        user_model = await user.get_user(
            session=session, username=created_user.username
        )
        assert user_model
        assert user_model == created_user

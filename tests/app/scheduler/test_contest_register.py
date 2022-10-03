import pytest


pytestmark = pytest.mark.asyncio


class TestCheckRegistration:
    def test_check_registration_no_contest(self, mocker):
        mocker.patch(
            'app.scheduler.contest_register.get_contest',
            return_value=None,
        )
        # assert contest_register.check_registration() is None
        assert False

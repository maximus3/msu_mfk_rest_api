# pylint: disable=duplicate-code

import pytest
from sqlalchemy import select

from app.database.models import StudentContest
from app.scheduler import contest_register


pytestmark = pytest.mark.asyncio


class TestCheckRegistration:
    @staticmethod
    async def check_relation(student_model, contest_model, session):
        student_contest = (
            await session.execute(
                select(StudentContest)
                .where(StudentContest.contest_id == contest_model.id)
                .where(StudentContest.student_id == student_model.id)
            )
        ).scalar_one_or_none()
        return student_contest

    @pytest.mark.usefixtures(
        'mock_make_request_to_yandex_contest', 'student_contest'
    )
    async def test_check_registration_already_registered(
        self, session, created_contest, created_student
    ):
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is not None
        )
        assert (
            await contest_register.check_registration(
                session, created_contest, created_student
            )
            is False
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [404, 500, 401, 403, 200, 201, 409],
        indirect=True,
    )
    async def test_add_student_to_contest_404(
        self,
        mock_make_request_to_yandex_contest,
        session,
        created_contest,
        created_student,
    ):
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is None
        )
        result_check = await contest_register.check_registration(
            session, created_contest, created_student
        )
        relation_created = await self.check_relation(
            created_student, created_contest, session
        )
        if mock_make_request_to_yandex_contest.return_value.status_code in [
            409,
            200,
            201,
        ]:
            assert result_check
            assert relation_created
        else:
            assert not result_check
            assert relation_created is None

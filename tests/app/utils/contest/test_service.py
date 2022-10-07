# pylint: disable=unused-argument

import pytest
from sqlalchemy import select

from app.database.models import StudentContest
from app.utils import contest


pytestmark = pytest.mark.asyncio


class TestAddStudentToContest:
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

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [404],
        indirect=True,
    )
    async def test_add_student_to_contest_404(
        self,
        mock_make_request_to_yandex_contest,
        session,
        potential_contest,
        created_student,
    ):
        assert (
            await self.check_relation(
                created_student, potential_contest, session
            )
            is None
        )
        assert await contest.add_student_to_contest(
            session, potential_contest, created_student
        ) == (
            False,
            f'Contest {potential_contest.yandex_contest_id} not found',
        )
        assert (
            await self.check_relation(
                created_student, potential_contest, session
            )
            is None
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [409],
        indirect=True,
    )
    async def test_add_student_to_contest_409(
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
        assert await contest.add_student_to_contest(
            session, created_contest, created_student
        ) == (True, None)
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is not None
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [200],
        indirect=True,
    )
    async def test_add_student_to_contest_200(
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
        assert await contest.add_student_to_contest(
            session, created_contest, created_student
        ) == (True, None)
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is not None
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [201],
        indirect=True,
    )
    async def test_add_student_to_contest_201(
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
        assert await contest.add_student_to_contest(
            session, created_contest, created_student
        ) == (True, None)
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is not None
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [401],
        indirect=True,
    )
    async def test_add_student_to_contest_401(
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
        assert await contest.add_student_to_contest(
            session, created_contest, created_student
        ) == (False, 'Yandex API key is invalid. Please check it in .env file')
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is None
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [403],
        indirect=True,
    )
    async def test_add_student_to_contest_403(
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
        assert await contest.add_student_to_contest(
            session, created_contest, created_student
        ) == (
            False,
            'Yandex API key does not have access to the contest '
            f'"{created_contest.yandex_contest_id}"',
        )
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is None
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [500],
        indirect=True,
    )
    async def test_add_student_to_contest_500(
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
        assert await contest.add_student_to_contest(
            session, created_contest, created_student
        ) == (False, 'Unknown error. Status code: 500')
        assert (
            await self.check_relation(
                created_student, created_contest, session
            )
            is None
        )


class TestGetProblems:
    pass


class TestGetParticipantsLoginToId:
    pass


class Test_AddResults:
    pass


class TestGetOkSubmissions:
    pass

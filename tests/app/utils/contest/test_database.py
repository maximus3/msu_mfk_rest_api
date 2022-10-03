# pylint: disable=unused-argument

from uuid import uuid4

import pytest
from sqlalchemy import select

from app.database.models import StudentContest
from app.utils import contest


pytestmark = pytest.mark.asyncio


class TestGetAllContestsHandler:
    async def test_get_all_contests_empty(self, session):
        assert await contest.get_all_contests(session) == []

    async def test_get_all_contests(self, session, created_contest):
        assert await contest.get_all_contests(session) == [created_contest]

    async def test_get_all_contests_multiple(
        self, session, created_two_contests
    ):
        assert sorted(
            await contest.get_all_contests(session), key=lambda x: x.id
        ) == sorted(created_two_contests, key=lambda x: x.id)


class TestGetContestsHandler:
    async def test_get_contests_empty(self, session, created_course):
        assert (
            await contest.get_contests(
                session=session, course_id=created_course.id
            )
            == []
        )

    async def test_get_contests(self, session, created_contest):
        assert await contest.get_contests(
            session=session, course_id=created_contest.course_id
        ) == [created_contest]

    async def test_get_contests_multiple(self, session, created_two_contests):
        assert sorted(
            await contest.get_contests(
                session=session, course_id=created_two_contests[0].course_id
            ),
            key=lambda x: x.id,
        ) == sorted(created_two_contests, key=lambda x: x.id)

    async def test_get_contests_only_needed_course(
        self, session, created_two_contests, created_two_courses
    ):
        assert sorted(
            await contest.get_contests(
                session=session, course_id=created_two_contests[0].course_id
            ),
            key=lambda x: x.id,
        ) == sorted(created_two_contests, key=lambda x: x.id)

        assert (
            await contest.get_contests(
                session=session, course_id=created_two_courses[1].id
            )
            == []
        )


class TestIsStudentRegisteredOnContestHandler:
    async def test_is_student_registered_on_contest_no_contest(
        self, session, created_student
    ):
        assert (
            await contest.is_student_registered_on_contest(
                session=session,
                contest_id=uuid4(),
                student_id=created_student.id,
            )
            is False
        )

    async def test_is_student_registered_on_contest_no_student(
        self, session, created_contest
    ):
        assert (
            await contest.is_student_registered_on_contest(
                session=session,
                contest_id=created_contest.id,
                student_id=uuid4(),
            )
            is False
        )

    async def test_is_student_registered_on_contest_no_relation(
        self, session, created_contest, created_student
    ):
        assert (
            await contest.is_student_registered_on_contest(
                session=session,
                contest_id=created_contest.id,
                student_id=created_student.id,
            )
            is False
        )

    async def test_is_student_registered_on_contest_ok(
        self, session, created_contest, created_student, student_contest
    ):
        assert (
            await contest.is_student_registered_on_contest(
                session=session,
                contest_id=created_contest.id,
                student_id=created_student.id,
            )
            is True
        )


class TestAddStudentContestRelationHandler:
    async def test_add_student_contest_relation_ok(
        self, session, created_contest, created_student
    ):
        await contest.add_student_contest_relation(
            session=session,
            contest_id=created_contest.id,
            student_id=created_student.id,
            course_id=created_contest.course_id,
        )
        student_contest = (
            await session.execute(
                select(StudentContest)
                .where(StudentContest.contest_id == created_contest.id)
                .where(StudentContest.student_id == created_student.id)
            )
        ).scalar_one_or_none()
        assert student_contest

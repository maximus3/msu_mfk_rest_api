# pylint: disable=duplicate-code,too-many-arguments,unused-argument,too-many-nested-blocks

import loguru
import pytest
from sqlalchemy import select

from app.database.models import StudentContest
from app.scheduler.contest_register import (
    check_students_for_contest_registration,
    register_student,
)


pytestmark = pytest.mark.asyncio


@pytest.mark.xfail  # TODO: remove
class BaseHandler:
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


@pytest.mark.usefixtures('mock_bot')
class TestRegisterStudentHandler(BaseHandler):
    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [404, 500, 401, 403, 200, 201, 409],
        indirect=True,
    )
    async def test_register_student(
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
        result_check = await register_student(
            session,
            created_contest,
            created_student,
            logger=loguru.logger,
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


@pytest.mark.usefixtures('mock_bot')
class TestCheckStudentsForContestRegistrationHandler(BaseHandler):
    @classmethod
    async def assert_four_relations(
        cls, session, contest_batches, student_batches, result, result_in=None
    ):
        cur = 0

        for contest_batch in contest_batches:
            for student_batch in student_batches:
                cur_in = cur in (0, 3)
                res = result[cur]

                for contest_model in contest_batch:
                    for student_model in student_batch:
                        if result_in and cur_in:
                            assert await cls.check_relation(
                                student_model, contest_model, session
                            )
                        elif res is None:
                            assert (
                                await cls.check_relation(
                                    student_model, contest_model, session
                                )
                                is None
                            )
                        else:
                            assert await cls.check_relation(
                                student_model, contest_model, session
                            )
                        cur_in = False

                cur += 1

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [404, 500, 401, 403, 200, 201, 409],
        indirect=True,
    )
    async def test_check_students_for_contest_registration_ok(
        self,
        session,
        created_course,
        created_two_contests,
        created_two_students_with_course,
        mock_make_request_to_yandex_contest,
    ):
        for contest_model in created_two_contests:
            for student_model in created_two_students_with_course:
                assert (
                    await self.check_relation(
                        student_model, contest_model, session
                    )
                    is None
                )
        await check_students_for_contest_registration(
            session,
            created_course,
            base_logger=loguru.logger,
        )
        for contest_model in created_two_contests:
            for student_model in created_two_students_with_course:
                if (
                    mock_make_request_to_yandex_contest.return_value.status_code  # pylint: disable=line-too-long
                    in [409, 200, 201]
                ):
                    assert await self.check_relation(
                        student_model, contest_model, session
                    )
                else:
                    assert (
                        await self.check_relation(
                            student_model, contest_model, session
                        )
                        is None
                    )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [404, 500, 401, 403, 200, 201, 409],
        indirect=True,
    )
    async def test_check_students_for_contest_registration_ok_two_courses(
        self,
        session,
        created_two_courses,
        created_four_contests_for_two_courses,
        created_four_students_for_two_courses,
        mock_make_request_to_yandex_contest,
    ):
        would_register = (
            True
            if mock_make_request_to_yandex_contest.return_value.status_code
            in [409, 200, 201]
            else None
        )
        await self.assert_four_relations(
            session,
            created_four_contests_for_two_courses,
            created_four_students_for_two_courses,
            [None, None, None, None],
        )
        await check_students_for_contest_registration(
            session, created_two_courses[0], base_logger=loguru.logger
        )
        await self.assert_four_relations(
            session,
            created_four_contests_for_two_courses,
            created_four_students_for_two_courses,
            [would_register, None, None, None],
        )
        await check_students_for_contest_registration(
            session, created_two_courses[1], base_logger=loguru.logger
        )
        await self.assert_four_relations(
            session,
            created_four_contests_for_two_courses,
            created_four_students_for_two_courses,
            [would_register, None, None, would_register],
        )

    @pytest.mark.parametrize(
        'mock_make_request_to_yandex_contest',
        [404, 500, 401, 403, 200, 201, 409],
        indirect=True,
    )
    async def test_check_students_for_contest_registration_ok_two_courses_some_registered(  # pylint: disable=line-too-long
        self,
        session,
        created_two_courses,
        created_four_contests_for_two_courses,
        created_four_students_for_two_courses,
        created_relations_one_student_on_one_contest,
        mock_make_request_to_yandex_contest,
    ):
        would_register = (
            True
            if mock_make_request_to_yandex_contest.return_value.status_code
            in [409, 200, 201]
            else None
        )
        await self.assert_four_relations(
            session,
            created_four_contests_for_two_courses,
            created_four_students_for_two_courses,
            [None, None, None, None],
            True,
        )
        await check_students_for_contest_registration(
            session, created_two_courses[0], base_logger=loguru.logger
        )
        await self.assert_four_relations(
            session,
            created_four_contests_for_two_courses,
            created_four_students_for_two_courses,
            [would_register, None, None, None],
            True,
        )
        await check_students_for_contest_registration(
            session, created_two_courses[1], base_logger=loguru.logger
        )
        await self.assert_four_relations(
            session,
            created_four_contests_for_two_courses,
            created_four_students_for_two_courses,
            [would_register, None, None, would_register],
            True,
        )

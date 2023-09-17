# pylint: disable=unused-argument,line-too-long,too-many-arguments

import pytest
from sqlalchemy import select

from app.database.models import StudentDepartment
from app.schemas import register as register_schemas
from app.utils import student


pytestmark = pytest.mark.asyncio


class TestGetStudentHandler:
    async def test_get_student_no_student(self, session, potential_student):
        assert (
            await student.get_student(
                session=session, contest_login=potential_student.contest_login
            )
            is None
        )

    async def test_get_student_ok(self, session, created_student):
        student_model = await student.get_student(
            session=session, contest_login=created_student.contest_login
        )
        assert student_model
        assert student_model == created_student


class TestGetStudentsByCourseHandler:
    async def test_get_students_by_course_no_students(
        self, session, created_course
    ):
        assert (
            await student.get_students_by_course(
                session=session, course_id=created_course.id
            )
            == []
        )

    async def test_get_students_by_course_no_relation(
        self, session, created_course, created_student
    ):
        assert (
            await student.get_students_by_course(
                session=session, course_id=created_course.id
            )
            == []
        )

    async def test_get_students_by_course_ok(
        self, session, created_course, created_student, student_course
    ):
        assert await student.get_students_by_course(
            session=session, course_id=created_course.id
        ) == [created_student]


class TestGetStudentsByCourseWithNoContestHandler:
    async def test_get_students_by_course_with_no_contest_no_students(
        self, session, created_course, created_contest
    ):
        assert (
            await student.get_students_by_course_with_no_contest(
                session=session,
                course_id=created_course.id,
                contest_id=created_contest.id,
            )
            == []
        )

    async def test_get_students_by_course_with_no_contest_no_relation_course(
        self, session, created_course, created_contest, created_student
    ):
        assert (
            await student.get_students_by_course_with_no_contest(
                session=session,
                course_id=created_course.id,
                contest_id=created_contest.id,
            )
            == []
        )

    async def test_get_students_by_course_with_no_contest_no_relation(
        self,
        session,
        created_course,
        created_contest,
        created_student,
        student_course,
    ):
        assert await student.get_students_by_course_with_no_contest(
            session=session,
            course_id=created_course.id,
            contest_id=created_contest.id,
        ) == [created_student]

    async def test_get_students_by_course_with_no_contest_ok(
        self,
        session,
        created_course,
        created_contest,
        created_student,
        student_course,
        student_contest,
    ):
        assert (
            await student.get_students_by_course_with_no_contest(
                session=session,
                course_id=created_course.id,
                contest_id=created_contest.id,
            )
            == []
        )

    async def test_get_students_by_course_with_no_contest_ok_many(
        self,
        session,
        created_course,
        created_contest,
        created_two_students_with_course,
    ):
        assert sorted(
            await student.get_students_by_course_with_no_contest(
                session=session,
                course_id=created_course.id,
                contest_id=created_contest.id,
            ),
            key=lambda x: x.id,
        ) == sorted(created_two_students_with_course, key=lambda x: x.id)

    async def test_get_students_by_course_with_no_contest_ok_many_no_registered(
        self,
        session,
        created_two_courses,
        created_four_contests_for_two_courses,
        created_four_students_for_two_courses,
    ):
        for course_num in range(2):
            for contest_num in range(2):
                assert sorted(
                    await student.get_students_by_course_with_no_contest(
                        session=session,
                        course_id=created_two_courses[course_num].id,
                        contest_id=created_four_contests_for_two_courses[
                            course_num
                        ][contest_num].id,
                    ),
                    key=lambda x: x.id,
                ) == sorted(
                    created_four_students_for_two_courses[course_num],
                    key=lambda x: x.id,
                )

    async def test_get_students_by_course_with_no_contest_ok_many_some_registered(
        self,
        session,
        created_two_courses,
        created_four_contests_for_two_courses,
        created_four_students_for_two_courses,
        created_relations_one_student_on_one_contest,
    ):
        for course_num in range(2):
            for contest_num in range(2):
                assert sorted(
                    await student.get_students_by_course_with_no_contest(
                        session=session,
                        course_id=created_two_courses[course_num].id,
                        contest_id=created_four_contests_for_two_courses[
                            course_num
                        ][contest_num].id,
                    ),
                    key=lambda x: x.id,
                ) == sorted(
                    created_four_students_for_two_courses[course_num][
                        (contest_num == 0) :
                    ],
                    key=lambda x: x.id,
                )


class TestGetStudentsByCourseWithDepartmentHandler:
    async def test_get_students_by_course_with_department_no_students(
        self, session, created_course, created_department
    ):
        assert (
            await student.get_students_by_course_with_department(
                session=session,
                course_id=created_course.id,
            )
            == []
        )

    async def test_get_students_by_course_with_department_no_relations(
        self, session, created_course, created_department, created_student
    ):
        assert (
            await student.get_students_by_course_with_department(
                session=session,
                course_id=created_course.id,
            )
            == []
        )

    async def test_get_students_by_course_with_department_no_department_relation(
        self,
        session,
        created_course,
        created_department,
        created_student,
        student_course,
    ):
        assert await student.get_students_by_course_with_department(
            session=session,
            course_id=created_course.id,
        ) == [(created_student, student_course, None)]

    async def test_get_students_by_course_with_department_ok(
        self,
        session,
        created_course,
        created_department,
        created_student,
        student_course,
        student_department,
    ):
        assert await student.get_students_by_course_with_department(
            session=session,
            course_id=created_course.id,
        ) == [(created_student, student_course, created_department)]


class TestCreateStudentHandler:
    async def test_create_student_ok(
        self, session, potential_student, created_department
    ):
        student_model = await student.create_student(
            session=session,
            data=register_schemas.RegisterRequest(
                fio=potential_student.fio,
                token=potential_student.token,
                department=created_department.name,
                course='ANY',
            ),
            headers_data=register_schemas.RegisterHeaders(
                contest_login=potential_student.contest_login,
                tg_id=potential_student.tg_id,
                tg_username=potential_student.tg_username,
                bm_id=potential_student.bm_id,
                yandex_id=potential_student.yandex_id,
            ),
            department=created_department,
        )
        assert student_model
        assert student_model.fio == potential_student.fio
        assert student_model.contest_login == potential_student.contest_login
        assert student_model.token == potential_student.token
        student_department = (
            await session.execute(
                select(StudentDepartment)
                .where(StudentDepartment.student_id == student_model.id)
                .where(
                    StudentDepartment.department_id == created_department.id
                )
            )
        ).scalar_one_or_none()
        assert student_department

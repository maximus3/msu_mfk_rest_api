# pylint: disable=unused-argument

import pytest
from sqlalchemy import select

from app.database.models import StudentDepartment
from app.schemas import RegisterRequest
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


class TestCreateStudentHandler:
    async def test_create_student_ok(
        self, session, potential_student, created_department
    ):
        student_model = await student.create_student(
            session=session,
            data=RegisterRequest(
                fio=potential_student.fio,
                contest_login=potential_student.contest_login,
                token=potential_student.token,
                department=created_department.name,
                course='ANY',
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

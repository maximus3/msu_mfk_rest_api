# pylint: disable=unused-argument
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.database.models import StudentCourse
from app.utils import course


pytestmark = pytest.mark.asyncio


class TestGetCourseHandler:
    async def test_get_course_no_course(self, session, potential_course):
        assert (
            await course.get_course(
                session=session, name=potential_course.name
            )
            is None
        )

    async def test_get_course_ok(self, session, created_course):
        course_model = await course.get_course(
            session=session, name=created_course.name
        )
        assert course_model
        assert course_model == created_course


class TestIsStudentRegisteredOnCourseHandler:
    async def test_is_student_registered_on_course_no_course(
        self, session, created_user
    ):
        assert (
            await course.is_student_registered_on_course(
                session=session,
                student_id=created_user.id,
                course_id=uuid4(),
            )
            is False
        )

    async def test_is_student_registered_on_course_no_student(
        self, session, created_course
    ):
        assert (
            await course.is_student_registered_on_course(
                session=session,
                student_id=uuid4(),
                course_id=created_course.id,
            )
            is False
        )

    async def test_is_student_registered_on_course_not_registered(
        self, session, created_user, created_course
    ):
        assert (
            await course.is_student_registered_on_course(
                session=session,
                student_id=created_user.id,
                course_id=created_course.id,
            )
            is False
        )

    async def test_is_student_registered_on_course_ok(
        self, session, created_student, created_course, student_course
    ):
        assert (
            await course.is_student_registered_on_course(
                session=session,
                student_id=created_student.id,
                course_id=created_course.id,
            )
            is True
        )


class TestAddStudentToCourseHandler:
    async def test_add_student_to_course_ok(
        self, session, created_student, created_course
    ):
        await course.add_student_to_course(
            session=session,
            student_id=created_student.id,
            course_id=created_course.id,
        )
        student_course = (
            await session.execute(
                select(StudentCourse)
                .where(StudentCourse.student_id == created_student.id)
                .where(StudentCourse.course_id == created_course.id)
            )
        ).scalar_one_or_none()
        assert student_course

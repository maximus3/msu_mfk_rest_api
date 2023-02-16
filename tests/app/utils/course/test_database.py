# pylint: disable=unused-argument

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


class TestGetAllActiveCoursesHandler:
    async def test_no_courses(self, session):
        assert await course.get_all_active_courses(session=session) == []

    async def test_ok(self, session, created_course):
        courses = await course.get_all_active_courses(session=session)
        assert courses
        assert len(courses) == 1
        assert courses[0] == created_course

    async def test_ok_multiple(self, session, created_two_courses):
        courses = await course.get_all_active_courses(session=session)
        assert courses
        assert len(courses) == 2
        assert sorted(courses, key=lambda x: x.name) == sorted(
            created_two_courses, key=lambda x: x.name
        )

    async def test_ok_multiple_archive(
        self, session, created_two_courses_with_archive
    ):
        courses = await course.get_all_active_courses(session=session)
        assert courses
        assert len(courses) == 1
        assert courses[0].name == created_two_courses_with_archive[1].name

    async def test_ok_multiple_closed_registration(
        self, session, created_two_courses_with_closed_registration
    ):
        courses = await course.get_all_active_courses(session=session)
        assert courses
        assert len(courses) == 2
        assert sorted(courses, key=lambda x: x.name) == sorted(
            created_two_courses_with_closed_registration, key=lambda x: x.name
        )


class TestGetAllCoursesWithOpenRegistrationHandler:
    async def test_no_courses(self, session):
        assert (
            await course.get_all_courses_with_open_registration(
                session=session
            )
            == []
        )

    async def test_ok(self, session, created_course):
        courses = await course.get_all_courses_with_open_registration(
            session=session
        )
        assert courses
        assert len(courses) == 1
        assert courses[0] == created_course

    async def test_ok_multiple(self, session, created_two_courses):
        courses = await course.get_all_courses_with_open_registration(
            session=session
        )
        assert courses
        assert len(courses) == 2
        assert sorted(courses, key=lambda x: x.name) == sorted(
            created_two_courses, key=lambda x: x.name
        )

    async def test_ok_multiple_archive(
        self, session, created_two_courses_with_archive
    ):
        courses = await course.get_all_courses_with_open_registration(
            session=session
        )
        assert courses
        assert len(courses) == 1
        assert courses[0].name == created_two_courses_with_archive[1].name

    async def test_ok_multiple_closed_registration(
        self, session, created_two_courses_with_closed_registration
    ):
        courses = await course.get_all_courses_with_open_registration(
            session=session
        )
        assert courses
        assert len(courses) == 1
        assert (
            courses[0].name
            == created_two_courses_with_closed_registration[1].name
        )


class TestIsStudentRegisteredOnCourseHandler:
    async def test_is_student_registered_on_course_no_course(
        self, session, created_user, potential_course
    ):
        assert (
            await course.is_student_registered_on_course(
                session=session,
                student_id=created_user.id,
                course_id=potential_course.id,
            )
            is False
        )

    async def test_is_student_registered_on_course_no_student(
        self, session, created_course, potential_student
    ):
        assert (
            await course.is_student_registered_on_course(
                session=session,
                student_id=potential_student.id,
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

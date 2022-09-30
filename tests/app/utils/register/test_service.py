import pytest
from sqlalchemy import select

from app.database.models import Student, StudentCourse
from app.schemas import RegisterRequest, DatabaseStatus
from app.utils import register

pytestmark = pytest.mark.asyncio


class TestRegisterStudentOnCourse:
    async def test_register_student_on_course_already_registered(
            self, session, created_student, created_course, created_department, student_course, student_department
    ):
        data = RegisterRequest(
            fio=created_student.fio,
            department=created_department.name,
            contest_login=created_student.contest_login,
            course=created_course.name,
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.ALREADY_EXISTS
        assert message == 'Student already registered on course'

    async def test_register_student_on_course_already_registered_second_query(
            self, session, created_student, created_course, created_department, student_department
    ):
        data = RegisterRequest(
            fio=created_student.fio,
            department=created_department.name,
            contest_login=created_student.contest_login,
            course=created_course.name,
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.OK

        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.ALREADY_EXISTS
        assert message == 'Student already registered on course'

    async def test_register_student_on_course_not_found(
            self, session, created_student, created_department, student_department
    ):
        data = RegisterRequest(
            fio=created_student.fio,
            contest_login=created_student.contest_login,
            department=created_department.name,
            course='not found',
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.NOT_FOUND
        assert message == 'Course not found'

    async def test_register_student_on_course_department_not_found(
            self, session, created_student, created_course
    ):
        data = RegisterRequest(
            fio=created_student.fio,
            contest_login=created_student.contest_login,
            department='not found',
            course=created_course.name,
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.NOT_FOUND
        assert message == 'Department not found'

    async def test_register_student_on_course_department_not_found_without_student(
            self, session, created_course
    ):
        data = RegisterRequest(
            fio='fio',
            contest_login='contest_login',
            department='not found',
            course=created_course.name,
            token='token',
        )
        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.NOT_FOUND
        assert message == 'Department not found'

    async def test_register_student_on_course_ok_no_student(
            self, session, created_course, created_department, potential_student
    ):
        data = RegisterRequest(
            fio=potential_student.fio,
            contest_login=potential_student.contest_login,
            department=created_department.name,
            course=created_course.name,
            token=potential_student.token,
        )
        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.OK

        student_model = (
            await session.execute(
                select(Student).where(Student.contest_login == potential_student.contest_login)
            )
        ).scalar_one_or_none()
        assert student_model is not None
        assert student_model.fio == potential_student.fio
        assert student_model.token == potential_student.token

        student_course_model = (
            await session.execute(
                select(StudentCourse)
                .where(StudentCourse.student_id == student_model.id)
                .where(StudentCourse.course_id == created_course.id)
            )
        ).scalar_one_or_none()
        assert student_course_model is not None

    async def test_register_student_on_course_ok_student_exists(
            self, session, created_student, created_course, created_department
    ):
        data = RegisterRequest(
            fio=created_student.fio,
            contest_login=created_student.contest_login,
            department=created_department.name,
            course=created_course.name,
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(session, data)
        assert status == DatabaseStatus.OK

        student_course_model = (
            await session.execute(
                select(StudentCourse)
                .where(StudentCourse.student_id == created_student.id)
                .where(StudentCourse.course_id == created_course.id)
            )
        ).scalar_one_or_none()
        assert student_course_model is not None

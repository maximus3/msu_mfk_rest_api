# pylint: disable=too-many-arguments, unused-argument, duplicate-code
import loguru
import pytest
from sqlalchemy import select

from app.database.models import Student, StudentCourse
from app.schemas import DatabaseStatus
from app.schemas import register as register_schemas
from app.utils import register


pytestmark = pytest.mark.asyncio


class TestRegisterStudentOnCourse:
    @staticmethod
    def _get_headers_data(student):
        return register_schemas.RegisterHeaders(
            contest_login=student.contest_login,
            tg_id=student.tg_id,
            tg_username=student.tg_username,
            bm_id=student.bm_id,
        )

    async def test_register_student_on_course_already_registered(
        self,
        session,
        created_student,
        created_course,
        created_department,
        student_course,
        student_department,
    ):
        data = register_schemas.RegisterRequest(
            fio=created_student.fio,
            department=created_department.name,
            course=created_course.name,
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(created_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.ALREADY_EXISTS
        assert message == 'Student already registered on course'

    async def test_register_student_on_course_already_registered_second_query(
        self,
        session,
        created_student,
        created_course,
        created_department,
        student_department,
    ):
        data = register_schemas.RegisterRequest(
            fio=created_student.fio,
            department=created_department.name,
            course=created_course.name,
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(created_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.OK

        status, message = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(created_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.ALREADY_EXISTS
        assert message == 'Student already registered on course'

    async def test_register_student_on_course_not_found(
        self, session, created_student, created_department, student_department
    ):
        data = register_schemas.RegisterRequest(
            fio=created_student.fio,
            department=created_department.name,
            course='not found',
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(created_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.NOT_FOUND
        assert message == 'Course not found'

    async def test_register_student_on_course_department_not_found(
        self, session, created_student, created_course
    ):
        data = register_schemas.RegisterRequest(
            fio=created_student.fio,
            department='not found',
            course=created_course.name,
            token=created_student.token,
        )
        status, message = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(created_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.NOT_FOUND
        assert message == 'Department not found'

    async def test_register_student_on_course_department_not_found_no_student(
        self, session, created_course, potential_student
    ):
        data = register_schemas.RegisterRequest(
            fio=potential_student.fio,
            department='not found',
            course=created_course.name,
            token=potential_student.token,
        )
        status, message = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(potential_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.NOT_FOUND
        assert message == 'Department not found'

    async def test_register_student_on_course_ok_no_student_no_tg_username(
        self, session, created_course, created_department, potential_student
    ):
        data = register_schemas.RegisterRequest(
            fio=potential_student.fio,
            department=created_department.name,
            course=created_course.name,
            token=potential_student.token,
        )
        headers_data = self._get_headers_data(potential_student)
        headers_data.tg_username = None
        status, _ = await register.register_student_on_course(
            session, data, headers_data=headers_data, logger=loguru.logger
        )
        assert status == DatabaseStatus.OK

        student_model = (
            await session.execute(
                select(Student).where(
                    Student.contest_login == potential_student.contest_login
                )
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

    async def test_register_student_on_course_ok_no_student(
        self, session, created_course, created_department, potential_student
    ):
        data = register_schemas.RegisterRequest(
            fio=potential_student.fio,
            department=created_department.name,
            course=created_course.name,
            token=potential_student.token,
        )
        status, _ = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(potential_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.OK

        student_model = (
            await session.execute(
                select(Student).where(
                    Student.contest_login == potential_student.contest_login
                )
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
        data = register_schemas.RegisterRequest(
            fio=created_student.fio,
            department=created_department.name,
            course=created_course.name,
            token=created_student.token,
        )
        status, _ = await register.register_student_on_course(
            session,
            data,
            headers_data=self._get_headers_data(created_student),
            logger=loguru.logger,
        )
        assert status == DatabaseStatus.OK

        student_course_model = (
            await session.execute(
                select(StudentCourse)
                .where(StudentCourse.student_id == created_student.id)
                .where(StudentCourse.course_id == created_course.id)
            )
        ).scalar_one_or_none()
        assert student_course_model is not None

    async def test_ok_student_exists_with_another_login(
        self, session, created_student, created_course, created_department
    ):
        was_login = created_student.contest_login
        data = register_schemas.RegisterRequest(
            fio=created_student.fio,
            department=created_department.name,
            course=created_course.name,
            token=created_student.token,
        )
        headers_data = self._get_headers_data(created_student)
        headers_data.contest_login = headers_data.contest_login + '_new'
        status, _ = await register.register_student_on_course(
            session, data, headers_data=headers_data, logger=loguru.logger
        )
        assert status == DatabaseStatus.OK

        student_course_model = (
            await session.execute(
                select(StudentCourse)
                .where(StudentCourse.student_id == created_student.id)
                .where(StudentCourse.course_id == created_course.id)
            )
        ).scalar_one_or_none()
        assert student_course_model is not None
        assert (
            await session.execute(
                select(Student).where(Student.id == created_student.id)
            )
        ).scalar().contest_login == was_login + '_new'

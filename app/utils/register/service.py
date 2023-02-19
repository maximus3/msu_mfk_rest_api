import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import DatabaseStatus, RegisterRequest
from app.utils.course import (
    add_student_to_course,
    get_course,
    is_student_registered_on_course,
)
from app.utils.department import get_department
from app.utils.student import create_student, get_student, get_student_by_token


async def register_student_on_course(
    session: AsyncSession, data: RegisterRequest, logger: 'loguru.Logger'
) -> tuple[DatabaseStatus, str]:
    department = await get_department(session, data.department)
    if department is None:
        logger.info(
            'Register request with department, that not exists: {}',
            data.department,
        )
        return DatabaseStatus.NOT_FOUND, 'Department not found'

    student = await get_student(session, data.contest_login)
    if student is None:
        logger.info(
            'Student {} not exists, checking token', data.contest_login
        )
        student = await get_student_by_token(session, data.token)
        if student is None:
            logger.info('No student with such login and token, creating')
            student = await create_student(session, data, department)
        else:
            logger.info(
                'Student has another prev login: {}, changing to {}',
                student.contest_login,
                data.contest_login,
            )
            student.contest_login = data.contest_login

    course = await get_course(session, data.course)
    if course is None:
        return DatabaseStatus.NOT_FOUND, 'Course not found'
    if not course.is_open_registration or course.is_archive:
        return DatabaseStatus.ERROR, 'Registration is closed'
    if await is_student_registered_on_course(session, student.id, course.id):
        return (
            DatabaseStatus.ALREADY_EXISTS,
            'Student already registered on course',
        )
    await add_student_to_course(session, student.id, course.id)
    await session.commit()
    return DatabaseStatus.OK, 'OK'

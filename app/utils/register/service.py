from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import DatabaseStatus, RegisterRequest
from app.utils.course import (
    add_student_to_course,
    get_course,
    is_student_registered_on_course,
)
from app.utils.student import create_student, get_student


async def register_student_on_course(
    session: AsyncSession, data: RegisterRequest
) -> tuple[DatabaseStatus, str]:
    student = await get_student(session, data.login)
    if student is None:
        status, message = await create_student(session, data)
        if status != DatabaseStatus.OK:
            return status, message
    student = await get_student(session, data.login)
    if student is None:
        return DatabaseStatus.ERROR, 'Student created, but not found'
    course = await get_course(session, data.course)
    if course is None:
        return DatabaseStatus.NOT_FOUND, 'Course not found'
    if await is_student_registered_on_course(session, student.id, course.id):
        return (
            DatabaseStatus.ALREADY_EXISTS,
            'Student already registered on course',
        )
    await add_student_to_course(session, student.id, course.id)
    await session.commit()
    return DatabaseStatus.OK, 'OK'

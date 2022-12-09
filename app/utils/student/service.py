import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.course import get_student_course

from .database import get_student_by_fio


async def get_student_course_is_ok(
    session: AsyncSession, course_id: UUID, fio: str
) -> bool:
    logger = logging.getLogger(__name__)
    student = await get_student_by_fio(session, fio)
    if student is None:
        logger.warning('No student with fio %s', fio)
        return False
    student_course = await get_student_course(session, student.id, course_id)
    if student_course is None:
        logger.warning(
            'Student %s (%s) is not registered on course %s',
            fio,
            student.id,
            course_id,
        )
        return False
    logger.info(
        'Student %s (%s) is registered on course %s',
        fio,
        student.id,
        course_id,
    )
    return student_course.is_ok

import typing as tp
from uuid import UUID

import loguru
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database import models
from app.utils.course import get_student_course

from .database import get_student, get_student_by_fio


async def get_student_course_is_ok(
    session: AsyncSession, course_id: UUID, fio: str, logger: 'loguru.Logger'
) -> bool:
    student = await get_student_by_fio(session, fio)
    if student is None:
        logger.warning('No student with fio {}', fio)
        return False
    student_course = await get_student_course(session, student.id, course_id)
    if student_course is None:
        logger.warning(
            'Student {} ({}) is not registered on course {}',
            fio,
            student.id,
            course_id,
        )
        return False
    logger.info(
        'Student {} ({}) is registered on course {}',
        fio,
        student.id,
        course_id,
    )
    return student_course.is_ok


async def get_student_or_raise(
    session: AsyncSession, contest_login: str, **kwargs: tp.Any
) -> models.Student:
    student = await get_student(session, contest_login)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Student not found',
            **kwargs,
        )
    return student

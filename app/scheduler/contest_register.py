# pylint: disable=too-many-nested-blocks

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import Course
from app.utils.contest import (
    add_student_to_contest,
    get_contests,
    is_student_registered_on_contest,
)
from app.utils.course import get_all_courses
from app.utils.student import get_students_by_course


async def check_students_for_contest_registration(
    session: AsyncSession, course: Course, logger: logging.Logger
) -> None:
    contests = await get_contests(session, course.id)
    students = await get_students_by_course(session, course.id)
    for contest in contests:
        logger.info('Contest: %s', contest)
        was_add = False
        for student in students:
            if not await is_student_registered_on_contest(
                session, student.id, contest.id
            ):
                was_add = True
                add_ok, message = await add_student_to_contest(
                    session,
                    contest,
                    student,
                    course.id,
                )
                if not add_ok:
                    logger.error(
                        'Student "%s" not registered on contest "%s". '
                        'Reason: %s',
                        student.contest_login,
                        contest.yandex_contest_id,
                        message,
                    )
                    continue
                await session.commit()
                logging.info(
                    'Student "%s" added to contest "%s"',
                    student.contest_login,
                    contest.yandex_contest_id,
                )
        if not was_add:
            logger.info(
                'No students added to contest "%s"', contest.yandex_contest_id
            )


async def job(
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await job(session=session)
    logger = logging.getLogger(__name__)
    courses = await get_all_courses(session)
    for course in courses:
        logger.info('Course: %s', course)
        await check_students_for_contest_registration(session, course, logger)


job_info = {
    'func': job,
    'trigger': 'interval',
    'minutes': 10,
}

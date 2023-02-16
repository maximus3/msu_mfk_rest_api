import logging
import traceback

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import Contest, Course, Student
from app.utils.contest import add_student_to_contest, get_contests
from app.utils.course import get_all_active_courses
from app.utils.student import get_students_by_course_with_no_contest


async def register_student(
    session: AsyncSession,
    contest: Contest,
    student: Student,
    logger: logging.Logger | None = None,
) -> bool:
    logger = logger or logging.getLogger(__name__)
    add_ok, message = await add_student_to_contest(
        session,
        contest,
        student,
    )
    if not add_ok:
        logger.error(
            'Student "%s" not registered on contest "%s". Reason: %s',
            student.contest_login,
            contest.yandex_contest_id,
            message,
        )
        return False
    await session.commit()
    logger.info(
        'Student "%s" added to contest "%s"',
        student.contest_login,
        contest.yandex_contest_id,
    )
    return True


async def check_students_for_contest_registration(
    session: AsyncSession, course: Course, logger: logging.Logger | None = None
) -> None:
    logger = logger or logging.getLogger(__name__)
    contests = await get_contests(session, course.id)
    logger.info('Course "%s" has %s contests', course.name, len(contests))
    for contest in contests:
        no_registered_students = await get_students_by_course_with_no_contest(
            session, course.id, contest.id
        )
        logger.info('Contest: %s', contest)
        logger.info(
            'Contest "%s" has %s no registered students',
            contest.yandex_contest_id,
            len(no_registered_students),
        )
        count = 0
        for student in no_registered_students:
            try:
                count += await register_student(
                    session, contest, student, logger
                )
            except Exception as e:  # pylint: disable=broad-except
                logger.exception(
                    'Error while register student "%s": %s', student, e
                )
                logger.error('%s', traceback.format_exc())
        logger.info(
            'Successfully added %s students to contest "%s"',
            count,
            contest.yandex_contest_id,
        )


async def job(
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await job(session=session)
    logger = logging.getLogger(__name__)
    courses = await get_all_active_courses(session)
    for course in courses:
        logger.info('Course: %s', course)
        await check_students_for_contest_registration(session, course, logger)


job_info = {
    'func': job,
    'trigger': 'interval',
    'minutes': 10,
    'name': 'contest_register',
}

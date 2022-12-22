# pylint: disable=too-many-lines,duplicate-code

import logging
import traceback

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_helper import send_message
from app.database.connection import SessionManager
from app.database.models import (
    Contest,
    Course,
    Department,
    Student,
    StudentContest,
    StudentCourse,
)
from app.m3tqdm import tqdm
from app.schemas import Level, Levels
from app.utils.contest import (
    get_contests,
    get_or_create_student_contest,
    get_student_best_submissions,
)
from app.utils.course import get_all_courses
from app.utils.scheduler import write_sql_tqdm
from app.utils.student import get_students_by_course_with_department


async def job() -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        courses = await get_all_courses(session)
    logger = logging.getLogger(__name__)
    async for course in tqdm(
        courses,
        name='contest_results_courses',
        logger=logger,
        sql_write_func=write_sql_tqdm,
    ):
        logger.info('Course: %s', course)
        try:
            await update_course_results(course, logger)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                'Error while updating course results for %s: %s',
                course.name,
                exc,
            )
            try:
                await send_message(
                    f'Error while updating course results for {course.name}'
                    f': {exc}\n{traceback.format_exc()}'
                )
            except Exception as send_exc:  # pylint: disable=broad-except
                logger.exception(
                    'Error while sending error message: %s', send_exc
                )
            continue

    await send_message(
        'Results updated',
        level='info',
    )


async def update_course_results(
    course: Course, logger: logging.Logger | None = None
) -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        contests = await get_contests(session, course.id)
        students_sc_departments = await get_students_by_course_with_department(
            session, course.id
        )
    logger = logger or logging.getLogger(__name__)
    is_all_results_ok = True
    contests.sort(key=lambda x: x.lecture)
    course_score_sum = 0
    async for contest in tqdm(
        contests,
        name='contest_results_contests',
        logger=logger,
        sql_write_func=write_sql_tqdm,
    ):
        logger.info('Contest: %s', contest)
        course_score_sum += contest.score_max

        await process_contest(
            students_sc_departments,
            contest,
            course,
            course_score_sum,
            logger=logger,
        )
    if not is_all_results_ok:
        logger.error('Not all results ok')
        raise RuntimeError('Not all results ok')


async def process_contest(  # pylint: disable=too-many-arguments
    students_sc_departments: list[tuple[Student, StudentCourse, Department]],
    contest: Contest,
    course: Course,
    course_score_sum: float,
    logger: logging.Logger | None = None,
    session: AsyncSession | None = None,
) -> None:
    logger = logger or logging.getLogger(__name__)
    contest_levels = Levels(**contest.levels) if contest.levels else None
    if contest_levels:
        contest_levels.levels = sorted(
            contest_levels.levels, key=lambda x: x.score_need
        )
    async for student, student_course, department in tqdm(
        students_sc_departments,
        name='contest_results_students',
        sql_write_func=write_sql_tqdm,
    ):
        try:
            await process_student(
                student,
                student_course,
                department,
                contest,
                course,
                contest_levels,
                course_score_sum,
                session,
                logger,
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                'Error while updating course results for '
                'course %s, contest %s, student %s: %s',
                course.name,
                contest.yandex_contest_id,
                student.contest_login,
                exc_info=exc,
            )
            try:
                await send_message(
                    f'Error while updating course results '
                    f'for course {course.name}, '
                    f'contest {contest.yandex_contest_id}, '
                    f'student {student.contest_login}: '
                    f'{exc}\n```{traceback.format_exc()}```'
                )
            except Exception as send_exc:  # pylint: disable=broad-except
                logger.exception(
                    'Error while sending error message: %s', send_exc
                )


async def process_student(  # pylint: disable=too-many-arguments
    student: Student,
    student_course: StudentCourse,
    department: Department,
    contest: Contest,
    course: Course,
    contest_levels: Levels | None,
    course_score_sum: float,
    session: AsyncSession | None = None,
    logger: logging.Logger | None = None,
) -> None:
    if student_course.is_ok:
        return
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await process_student(
                student,
                student_course,
                department,
                contest,
                course,
                contest_levels,
                course_score_sum,
                session=session,
                logger=logger,
            )
    logger = logger or logging.getLogger(__name__)
    student_contest = await get_or_create_student_contest(
        session,
        student.id,
        contest.id,
        course.id,
    )
    if student_contest.is_ok:
        return
    if student_contest.score == contest.score_max:
        logger.debug(
            'Student %s has already max score in contest %s',
            student.contest_login,
            contest.id,
        )
        return
    student_results = await get_student_best_submissions(
        contest,
        student,
        student_contest,
        course.short_name
        in ['ml_autumn_2022', 'da_autumn_2022'],  # TODO: magic constant
    )
    student_tasks_done = len(student_results)
    student_score = round(
        sum(submission.finalScore for submission in student_results),
        4,
    )  # TODO: magic constant
    student_score_no_deadline = round(
        sum(submission.noDeadlineScore for submission in student_results),
        4,
    )  # TODO: magic constant
    is_ok = student_score == contest.score_max
    is_ok_no_deadline = student_score == contest.score_max
    logger.info(
        'Student: %s, tasks done: %s, score: %s, is ok: %s',
        student.contest_login,
        student_tasks_done,
        student_score,
        is_ok,
    )
    if contest_levels and contest_levels.count > 0:
        levels_ok: list[Level] = list(
            filter(lambda level: level.name == 'Зачет', contest_levels.levels)
        )
        if len(levels_ok) == 0:
            levels_ok = contest_levels.levels
        is_ok = student_score >= min(level.score_need for level in levels_ok)

        levels_ok_no_deadline = list(
            filter(
                lambda level: level.name == 'Допуск к зачету',
                contest_levels.levels,
            )
        )
        if len(levels_ok_no_deadline) == 0:
            levels_ok_no_deadline = contest_levels.levels
        is_ok_no_deadline = student_score >= min(
            level.score_need for level in levels_ok_no_deadline
        )
    await update_student_contest_relation(
        student,
        contest,
        student_contest,
        student_tasks_done,
        student_score,
        student_score_no_deadline,
        is_ok,
        is_ok_no_deadline,
        session,
        logger,
    )


async def update_student_contest_relation(  # pylint: disable=too-many-arguments
    student: Student,
    contest: Contest,
    student_contest: StudentContest,
    student_tasks_done: int,
    student_score: float,
    student_score_no_deadline: float,
    is_ok: bool,
    is_ok_no_deadline: bool,
    session: AsyncSession | None = None,
    logger: logging.Logger | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await update_student_contest_relation(
                student,
                contest,
                student_contest,
                student_tasks_done,
                student_score,
                is_ok,
                is_ok_no_deadline,
                session,
                logger,
            )
    logger = logger or logging.getLogger(__name__)
    changes = False
    if student_contest.tasks_done < student_tasks_done:
        student_contest.tasks_done = student_tasks_done
        session.add(student_contest)
        changes = True
    if student_contest.score < student_score:
        student_contest.score = student_score
        session.add(student_contest)
        changes = True
    if student_contest.score_no_deadline < student_score_no_deadline:
        student_contest.score_no_deadline = student_score_no_deadline
        session.add(student_contest)
        changes = True
    if not student_contest.is_ok and is_ok:
        student_contest.is_ok = is_ok
        session.add(student_contest)
        changes = True
    if not student_contest.is_ok_no_deadline and is_ok_no_deadline:
        student_contest.is_ok_no_deadline = is_ok_no_deadline
        session.add(student_contest)
        changes = True
    if not changes:
        logger.info(
            'Student %s has no changes in contest %s',
            student.contest_login,
            contest.id,
        )


job_info = {
    'func': job,
    'trigger': 'interval',
    'hours': 1,
    'name': 'contest_results',
}

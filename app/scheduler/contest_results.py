# pylint: disable=duplicate-code,too-many-lines

# TODO: too many lines

import logging
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_helper.send import send_error_message, send_results
from app.database.connection import SessionManager
from app.database.models import Contest, Course, Department, Student
from app.schemas import ContestSubmissionFull, CourseResultsCSV, Levels
from app.utils.contest import (
    add_student_contest_relation,
    get_author_id,
    get_best_submissions,
    get_contests,
    get_student_contest_relation,
)
from app.utils.course import get_all_courses
from app.utils.student import get_students_by_course_with_department


async def save_to_csv(course_results: CourseResultsCSV, filename: str) -> None:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(','.join(course_results.keys))
        f.write('\n')
        for data in course_results.results.values():
            for i, key in enumerate(course_results.keys):
                f.write(f'{data.get(key, "")}')
                if i != len(course_results.keys) - 1:
                    f.write(',')
            f.write('\n')


async def fill_course_results(  # pylint: disable=too-many-arguments
    course_results: CourseResultsCSV,
    student: Student,
    department: Department,
    contest: Contest,
    student_score: float,
    is_ok: bool,
) -> None:
    course_results.results[student.contest_login][
        'contest_login'
    ] = student.contest_login
    course_results.results[student.contest_login]['fio'] = student.fio
    course_results.results[student.contest_login][
        'department'
    ] = department.name
    course_results.results[student.contest_login][
        f'lecture_{contest.lecture}_score'
    ] = student_score
    course_results.results[student.contest_login][
        f'lecture_{contest.lecture}'
    ] = is_ok
    course_results.results[student.contest_login][
        'ok'
    ] = is_ok and course_results.results[student.contest_login].get('ok', True)


async def get_author_id_update(
    student: Student,
    contest: Contest,
    session: AsyncSession | None = None,
    logger: logging.Logger | None = None,
) -> int:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await get_author_id_update(
                student,
                contest,
                session,
                logger,
            )
    logger = logger or logging.getLogger(__name__)
    student_contest = await get_student_contest_relation(
        session, student.id, contest.id
    )

    if student_contest is None:
        logger.warning(
            'Student %s has no relation with contest %s',
            student.contest_login,
            contest.id,
        )
        student_contest = await add_student_contest_relation(
            session,
            student.id,
            contest.id,
            contest.course_id,
            await get_author_id(
                student.contest_login, contest.yandex_contest_id
            ),
        )
    elif student_contest.author_id is None:
        logger.info(
            'Student %s has no author id in contest %s',
            student.contest_login,
            contest.id,
        )
        student_contest.author_id = await get_author_id(
            student.contest_login, contest.yandex_contest_id
        )
        session.add(student_contest)
    return student_contest.author_id


async def update_student_contest_relation(  # pylint: disable=too-many-arguments
    student: Student,
    contest: Contest,
    student_tasks_done: int,
    student_score: float,
    is_ok: bool,
    session: AsyncSession | None = None,
    logger: logging.Logger | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await update_student_contest_relation(
                student,
                contest,
                student_tasks_done,
                student_score,
                is_ok,
                session,
                logger,
            )
    logger = logger or logging.getLogger(__name__)
    student_contest = await get_student_contest_relation(
        session, student.id, contest.id
    )
    if student_contest is None:
        logger.warning(
            'Student %s has no relation with contest %s',
            student.contest_login,
            contest.id,
        )
        return
    if (
        student_contest.tasks_done != student_tasks_done
        or student_contest.score != student_score
        or student_contest.is_ok != is_ok
    ):
        student_contest.tasks_done = student_tasks_done
        student_contest.score = student_score
        student_contest.is_ok = is_ok
        session.add(student_contest)
    else:
        logger.info(
            'Student %s has no changes in contest %s',
            student.contest_login,
            contest.id,
        )


async def process_contest(  # pylint: disable=too-many-arguments
    students_and_departments: list[tuple[Student, Department]],
    results: list[ContestSubmissionFull],
    contest: Contest,
    course_results: CourseResultsCSV,
    logger: logging.Logger | None = None,
    session: AsyncSession | None = None,
) -> None:
    logger = logger or logging.getLogger(__name__)
    contest_levels = Levels(**contest.levels) if contest.levels else None
    if contest_levels:
        contest_levels.levels = sorted(
            contest_levels.levels, key=lambda x: x.score_need
        )
    for student, department in students_and_departments:
        author_id = await get_author_id_update(
            student, contest, logger=logger
        )  # TODO: many queries to db
        student_tasks_done = sum(
            True for submission in results if submission.authorId == author_id
        )
        student_score = round(
            sum(
                submission.finalScore
                for submission in results
                if submission.authorId == author_id
            ),
            4,
        )  # TODO: magic constant
        is_ok = student_tasks_done == contest.tasks_count
        logger.info(
            'Student: %s, tasks done: %s, score: %s, is ok: %s',
            student.contest_login,
            student_tasks_done,
            student_score,
            is_ok,
        )
        if contest_levels and contest_levels.count > 0:
            is_ok = student_score >= contest_levels.levels[0].score_need

        await fill_course_results(
            course_results,
            student,
            department,
            contest,
            student_score,
            is_ok,
        )

        await update_student_contest_relation(
            student,
            contest,
            student_tasks_done,
            student_score,
            is_ok,
            session,
            logger,
        )

    course_results.keys.append(f'lecture_{contest.lecture}_score')
    course_results.keys.append(f'lecture_{contest.lecture}')


async def update_course_results(
    course: Course, logger: logging.Logger | None = None
) -> CourseResultsCSV:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        contests = await get_contests(session, course.id)
        students_and_departments = (
            await get_students_by_course_with_department(session, course.id)
        )
    logger = logger or logging.getLogger(__name__)
    course_results = CourseResultsCSV(
        keys=['contest_login', 'fio', 'department'],
        results=defaultdict(dict),
    )
    is_all_results_ok = True
    for contest in contests:
        logger.info('Contest: %s', contest)
        results, is_all_results = await get_best_submissions(contest)
        is_all_results_ok = is_all_results_ok and is_all_results
        await process_contest(
            students_and_departments,
            results,
            contest,
            course_results,
            logger,
        )
    course_results.keys.append('ok')
    if not is_all_results_ok:
        logger.error('Not all results ok')
        raise RuntimeError('Not all results ok')
    return course_results


async def job() -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        courses = await get_all_courses(session)
    logger = logging.getLogger(__name__)
    filenames = []
    for course in courses:
        logger.info('Course: %s', course)
        try:
            course_results = await update_course_results(course, logger)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                'Error while updating course results for %s: %s',
                course.name,
                exc,
            )
            try:
                await send_error_message(
                    f'Error while updating course results for {course.name}'
                    f': {exc}\n{traceback.format_exc()}'
                )
            except Exception as send_exc:  # pylint: disable=broad-except
                logger.exception(
                    'Error while sending error message: %s', send_exc
                )
            continue
        filename = (
            f'results_{course.short_name}_'
            f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        )
        await save_to_csv(course_results, filename)
        filenames.append(filename)

    try:
        await send_results(filenames)
    except Exception as e:
        logger.error('Error while sending results: %s', e)
        raise e
    finally:
        for filename in filenames:
            Path(filename).unlink()


job_info = {
    'func': job,
    'trigger': 'interval',
    'hours': 1,
    'name': 'contest_results',
}

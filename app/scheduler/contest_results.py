# pylint: disable=duplicate-code

import logging
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_helper.send import send_error_message, send_results
from app.database.connection import SessionManager
from app.database.models import Contest, Course, Department, Student
from app.schemas import ContestResults, ContestSubmission
from app.utils.contest import (
    get_contests,
    get_ok_submissions,
    get_participants_login_to_id,
    get_student_contest_relation,
)
from app.utils.course import get_all_courses
from app.utils.student import get_students_by_course_with_department


async def save_to_csv(course_results: ContestResults, filename: str) -> None:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(','.join(course_results.keys))
        f.write('\n')
        for data in course_results.results.values():
            for i, key in enumerate(course_results.keys):
                f.write(f'{data.get(key, "")}')
                if i != len(course_results.keys) - 1:
                    f.write(',')
            f.write('\n')


async def process_contest(  # pylint: disable=too-many-arguments
    students_and_departments: list[tuple[Student, Department]],
    login_to_id: dict[str, int],
    results: list[ContestSubmission],
    contest: Contest,
    course_results: ContestResults,
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await process_contest(
                students_and_departments,
                login_to_id,
                results,
                contest,
                course_results,
                session,
            )
    for student, department in students_and_departments:
        author_id = login_to_id.get(student.contest_login)
        student_tasks_done = sum(
            True for submission in results if submission.authorId == author_id
        )
        is_ok = student_tasks_done >= contest.tasks_need
        course_results.results[student.contest_login][
            'contest_login'
        ] = student.contest_login
        course_results.results[student.contest_login]['fio'] = student.fio
        course_results.results[student.contest_login][
            'department'
        ] = department.name
        course_results.results[student.contest_login][
            f'lecture_{contest.lecture}'
        ] = is_ok
        course_results.results[student.contest_login][
            'ok'
        ] = is_ok and course_results.results[student.contest_login].get(
            'ok', True
        )
        student_contest = await get_student_contest_relation(
            session, student.id, contest.id
        )
        if student_contest is not None:
            student_contest.tasks_done = student_tasks_done
            student_contest.is_ok = is_ok
            session.add(student_contest)

    course_results.keys.append(f'lecture_{contest.lecture}')


async def update_course_results(
    course: Course, logger: logging.Logger | None = None
) -> ContestResults:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        contests = await get_contests(session, course.id)
        students_and_departments = (
            await get_students_by_course_with_department(session, course.id)
        )
    logger = logger or logging.getLogger(__name__)
    course_results = ContestResults(
        keys=['contest_login', 'fio', 'department'],
        results=defaultdict(dict),
    )
    for contest in contests:
        logger.info('Contest: %s', contest)
        login_to_id = await get_participants_login_to_id(
            contest.yandex_contest_id
        )
        results = await get_ok_submissions(contest.yandex_contest_id)
        await process_contest(
            students_and_departments,
            login_to_id,
            results,
            contest,
            course_results,
        )
    course_results.keys.append('ok')
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

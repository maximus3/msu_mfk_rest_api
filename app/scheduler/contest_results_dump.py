# pylint: disable=too-many-statements

import logging
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from app.bot_helper import send_message
from app.bot_helper.send import send_results
from app.database.connection import SessionManager
from app.database.models import Course, StudentCourse
from app.schemas import CourseResultsCSV
from app.utils.course import get_all_courses, get_student_course
from app.utils.results import (
    get_student_course_results,
    update_student_course_results,
)
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


async def get_course_results(
    course: Course, logger: logging.Logger | None = None
) -> CourseResultsCSV:
    logger = logger or logging.getLogger(__name__)
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        students_departments_results = []
        for (
            student,
            department,
        ) in await get_students_by_course_with_department(session, course.id):
            student_course = await get_student_course(
                session,
                student.id,
                course.id,
            )
            if student_course is None:
                logger.warning(
                    'StudentCourse not found for student %s and course %s',
                    student.id,
                    course.id,
                )
                student_course = StudentCourse(
                    student_id=student.id,
                    course_id=course.id,
                )
                session.add(student_course)
            if not student_course.is_ok:
                await update_student_course_results(
                    student, course, student_course, session=session
                )
                await session.commit()
                student_results = await get_student_course_results(
                    student, course, student_course, session=session
                )
            students_departments_results.append(
                (student, department, student_results)
            )
    course_results = CourseResultsCSV(
        keys=['contest_login', 'fio', 'department'],
        results=defaultdict(dict),
    )

    keys_add = True

    # pylint: disable=too-many-nested-blocks
    for student, department, student_results in students_departments_results:
        course_results.results[student.contest_login][
            'contest_login'
        ] = student.contest_login
        course_results.results[student.contest_login]['fio'] = student.fio
        course_results.results[student.contest_login][
            'department'
        ] = department.name
        course_results.results[student.contest_login][
            'score_sum'
        ] = student_results.score_sum
        course_results.results[student.contest_login][
            'score_max'
        ] = student_results.score_max
        course_results.results[student.contest_login][
            'ok'
        ] = student_results.is_ok
        for contest_results in student_results.contests:
            course_results.results[student.contest_login][
                f'lecture_{contest_results.lecture}_score'
            ] = contest_results.score

            if contest_results.levels:
                for i, level in enumerate(contest_results.levels):
                    course_results.results[student.contest_login][
                        f'lecture_{contest_results.lecture}_level_{level.name}'
                    ] = contest_results.levels_ok[i]

            if keys_add:
                course_results.keys.append(
                    f'lecture_{contest_results.lecture}_score'
                )
                if contest_results.levels:
                    for level in contest_results.levels:
                        course_results.keys.append(
                            f'lecture_{contest_results.lecture}_'
                            f'level_{level.name}'
                        )
        keys_add = False

    course_results.keys.append('score_sum')
    course_results.keys.append('score_max')
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
            course_results = await get_course_results(course, logger=logger)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                'Error while getting course results for %s: %s',
                course.name,
                exc,
            )
            try:
                await send_message(
                    f'Error while getting course results for {course.name}'
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
    'hours': 3,
    'name': 'contest_results_dump',
}

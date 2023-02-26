# pylint: disable=too-many-statements

import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import loguru

from app import constants
from app.bot_helper import send
from app.bot_helper.send import send_results
from app.database.connection import SessionManager
from app.database.models import Course, CourseLevels
from app.m3tqdm import tqdm
from app.schemas import CourseResultsCSV
from app.schemas import scheduler as scheduler_schemas
from app.utils.course import (
    get_all_active_courses,
    get_course_levels,
    get_or_create_student_course_level,
)
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
    course: Course,
    course_levels: list[CourseLevels],
    base_logger: 'loguru.Logger',
) -> CourseResultsCSV:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        students_departments_results = []
        async for (student, student_course, department,) in tqdm(
            await get_students_by_course_with_department(session, course.id),
            name=job_info.name + '-students',
        ):
            logger = base_logger.bind(
                student={
                    'id': student.id,
                    'contest_login': student.contest_login,
                }
            )
            student_course_levels = [
                await get_or_create_student_course_level(
                    session, student.id, course.id, course_level.id
                )
                for course_level in course_levels
            ]
            await update_student_course_results(
                student,
                course,
                course_levels,
                student_course,
                student_course_levels,
                base_logger=logger,
                session=session,
            )
            await session.commit()
            student_results = await get_student_course_results(
                student,
                course,
                course_levels,
                student_course,
                student_course_levels,
                logger=logger,
                session=session,
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
        for contest_results in student_results.contests:
            course_results.results[student.contest_login][
                f'lecture_{contest_results.lecture}_score'
            ] = contest_results.score

            if contest_results.levels:
                for level in contest_results.levels:
                    course_results.results[student.contest_login][
                        f'lecture_{contest_results.lecture}_level_{level.name}'
                    ] = level.is_ok

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
        for course_level in student_results.course_levels:
            course_results.results[student.contest_login][
                f'level_{course_level.name}'
            ] = course_level.is_ok
            if keys_add:
                course_results.keys.append(f'level_{course_level.name}')
        keys_add = False

    course_results.keys.append('score_sum')
    course_results.keys.append('score_max')
    return course_results


async def job(base_logger: 'loguru.Logger') -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        courses = await get_all_active_courses(session)
        levels_by_course = [
            await get_course_levels(session, course.id) for course in courses
        ]
    filenames = []
    async for course, course_levels in tqdm(
        zip(courses, levels_by_course),
        total=len(courses),
        name=job_info.name + '-courses',
    ):
        # pylint: disable=duplicate-code
        logger = base_logger.bind(
            course={'id': course.id, 'short_name': course.short_name}
        )
        logger.info('Course: {}', course)
        # pylint: disable=duplicate-code
        try:
            course_results = await get_course_results(
                course, course_levels, base_logger=logger
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                'Error while getting course results for {}: {}',
                course.short_name,
                exc,
            )
            await send.send_traceback_message_safe(
                logger=logger,
                message=f'Error while getting course '
                f'results for {course.short_name}: {exc}',
                code=traceback.format_exc(),
            )
            continue
        filename = (
            f'results_{course.short_name}_'
            f'{datetime.now().strftime(constants.dt_format_filename)}.csv'
        )
        await save_to_csv(course_results, filename)
        filenames.append(filename)

    try:
        await send_results(filenames)
    except Exception as exc:
        base_logger.error('Error while sending results: {}', exc)
        raise exc
    finally:
        for filename in filenames:
            Path(filename).unlink()


job_info = scheduler_schemas.JobInfo(
    func=job,
    name='contest_results_dump',
    trigger='interval',
    hours=3,
    config=scheduler_schemas.JobConfig(send_logs=True),
)

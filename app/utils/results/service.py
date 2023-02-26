# pylint: disable=too-many-lines
import math

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app import constants
from app.database.models import (
    Course,
    CourseLevels,
    Student,
    StudentCourse,
    StudentCourseLevels,
)
from app.schemas import ContestResults, CourseLevelResults, CourseResults
from app.schemas import contest as contest_schemas
from app.schemas import course as course_schemas
from app.utils import contest as contest_utils
from app.utils.common import get_datetime_msk_tz


async def get_student_course_results(  # pylint: disable=too-many-arguments
    student: Student,
    course: Course,
    course_levels: list[CourseLevels],
    student_course: StudentCourse,
    student_course_levels: list[StudentCourseLevels],
    logger: 'loguru.Logger',
    session: AsyncSession,
) -> CourseResults:
    contests = []

    for contest, student_contest in sorted(
        await contest_utils.get_contests_with_relations(
            session,
            course.id,
            student.id,
        ),
        key=lambda x: x[0].lecture,
    ):
        name = f'Лекция {contest.lecture}'
        if contest.lecture == 999:
            name = 'Зачет 21.12.2022'
        if contest.lecture == 9999:
            name = 'Зачет 25.12.2022'
        if contest.lecture == 99999:
            name = 'Зачет 12.01.2023'

        contest_levels = await contest_utils.get_contest_levels(
            session, contest.id
        )
        contest_levels.sort(key=lambda x: (x.count_method, x.ok_threshold))
        student_contest_levels = [
            await contest_utils.get_or_create_student_contest_level(
                session, student.id, course.id, contest.id, level.id
            )
            for level in contest_levels
        ]

        contests.append(
            ContestResults(
                link=contest.link,
                tasks_count=contest.tasks_count,
                score_max=contest.score_max,
                levels_count=len(contest_levels),
                levels=[
                    {
                        'name': level.name,
                        'score_need': level.ok_threshold
                        if level.count_method
                        == contest_schemas.LevelCountMethod.ABSOLUTE
                        else math.ceil(
                            level.ok_threshold * contest.score_max / 100
                        ),
                    }
                    for level in contest_levels
                    if level.level_ok_method
                    == contest_schemas.LevelOkMethod.SCORE_SUM
                ],
                levels_ok=[
                    student_contest_level.is_ok
                    for student_contest_level in student_contest_levels
                ],
                lecture=contest.lecture,
                tasks_done=student_contest.tasks_done,
                score=student_contest.score,
                score_no_deadline=student_contest.score_no_deadline,
                is_ok=student_contest.is_ok,
                is_ok_no_deadline=student_contest.is_ok_no_deadline,
                is_necessary=contest_schemas.ContestTag.NECESSARY
                in contest.tags,
                is_final=contest_schemas.ContestTag.FINAL in contest.tags,
                name=name,
                updated_at=get_datetime_msk_tz(
                    student_contest.dt_updated
                ).strftime(
                    constants.dt_format,
                ),
                deadline=get_datetime_msk_tz(contest.deadline).strftime(
                    constants.dt_format,
                ),
            )
        )

    if course.ok_method == course_schemas.LevelOkMethod.CONTESTS_OK:
        perc_ok = student_course.contests_ok_percent
    elif course.ok_method == course_schemas.LevelOkMethod.SCORE_SUM:
        perc_ok = student_course.score_percent
    else:
        logger.error(
            'Unknown ok_method: {}',
            course.ok_method,
        )
        raise ValueError(f'Unknown ok_method: {course.ok_method}')

    logger.info(
        'Student {} has course result',
        student.contest_login,
    )

    return CourseResults(
        name=course.name,
        contests=contests,
        score_sum=student_course.score,
        score_max=course.score_max,
        is_ok=student_course.is_ok,
        is_ok_final=student_course.is_ok_final,
        perc_ok=int(perc_ok),
        str_need='',
        course_levels=[
            CourseLevelResults(
                name=level.level_name,
                is_ok=sc_level.is_ok,
            )
            for level, sc_level in zip(course_levels, student_course_levels)
        ],
    )


async def update_student_course_results(  # pylint: disable=too-many-statements
    student: Student,
    course: Course,
    student_course: StudentCourse,
    logger: 'loguru.Logger',
    session: AsyncSession,
) -> None:
    course_score_sum = 0
    necessary_contests_results = []

    for (
        contest,
        student_contest,
    ) in await contest_utils.get_contests_with_relations(
        session,
        course.id,
        student.id,
    ):
        course_score_sum += student_contest.score

        if contest_schemas.ContestTag.NECESSARY in contest.tags:
            necessary_contests_results.append(student_contest.is_ok)

    count_necessary_contests = len(necessary_contests_results)
    contests_ok = sum(necessary_contests_results)
    contests_ok_percent = 100 * contests_ok / count_necessary_contests
    score_percent = 100 * course_score_sum / course.score_max
    if course.ok_method == 'contests_ok':
        perc_ok = contests_ok_percent
    elif course.ok_method == 'score_sum':
        perc_ok = score_percent
    else:
        logger.error('Unknown ok_method: {}', course.ok_method)
        raise ValueError(f'Unknown ok_method: {course.ok_method}')

    is_ok = perc_ok >= course.ok_threshold_perc

    if student_course.score < course_score_sum:
        student_course.score = course_score_sum
        session.add(student_course)
    if student_course.contests_ok < contests_ok:
        student_course.contests_ok = contests_ok
        session.add(student_course)
    if student_course.contests_ok_percent < contests_ok_percent:
        student_course.contests_ok_percent = contests_ok_percent
        session.add(student_course)
    if student_course.score_percent < score_percent:
        student_course.score_percent = score_percent
        session.add(student_course)
    if not student_course.is_ok and is_ok:
        student_course.is_ok = is_ok
        session.add(student_course)


async def update_sc_results_final(  # pylint: disable=too-many-statements,too-many-arguments,too-many-branches  # noqa: C901
    student: Student,
    course: Course,
    course_levels: list[CourseLevels],
    student_course: StudentCourse,
    student_course_levels: list[StudentCourseLevels],
    logger: 'loguru.Logger',
    session: AsyncSession,
) -> None:
    course_score_sum = 0
    course_score_sum_with_deadline = 0
    contests_results = []
    final_results = []

    levels_result_dict: dict[str, bool] = {
        level.level_name: True for level in course_levels
    }

    for (  # pylint: disable=too-many-nested-blocks
        contest,
        student_contest,
    ) in await contest_utils.get_contests_with_relations(
        session,
        course.id,
        student.id,
    ):
        if contest_schemas.ContestTag.FINAL in contest.tags:
            final_results.append(student_contest.is_ok)
        else:
            contests_results.append(student_contest.is_ok_no_deadline)
            course_score_sum += student_contest.score_no_deadline
            course_score_sum_with_deadline += student_contest.score

            if contest_schemas.ContestTag.NECESSARY in contest.tags:
                for level in course_levels:
                    if level.level_ok_method == 'contests_ok':
                        level_names = (
                            [
                                contest_level['name']
                                for contest_level in contest.levels['levels']
                            ]
                            if contest.levels
                            else []
                        )
                        k = level_names.index(level.contest_ok_level_name)
                        if k > -1:
                            levels_result_dict[level.level_name] = (
                                levels_result_dict[level.level_name]
                                and student_contest.score
                                >= contest.levels['levels'][k]['score_need']
                            )
                        else:
                            levels_result_dict[level.level_name] = False
                            logger.error(
                                'Contest {} has no level {}',
                                contest.name,
                                level.name,
                            )
                    elif level.level_ok_method == 'score_sum':
                        pass
                    else:
                        raise ValueError(
                            f'Unknown level_ok_method: '
                            f'{level.level_ok_method}',
                        )

    for level, sc_level in zip(course_levels, student_course_levels):
        if level.level_ok_method == 'score_sum':
            levels_result_dict[level.level_name] = (
                student_course.score >= level.ok_threshold
            )
        if sc_level.is_ok != levels_result_dict[level.level_name]:
            sc_level.is_ok = levels_result_dict[level.level_name]
            session.add(sc_level)

    count_contests = len(contests_results)
    contests_ok = sum(contests_results)
    contests_ok_percent = 100 * contests_ok / count_contests
    score_percent = 100 * course_score_sum / course.score_max
    if course.ok_method == 'contests_ok':
        perc_ok = contests_ok_percent
    elif course.ok_method == 'score_sum':
        perc_ok = score_percent
    else:
        logger.error('Unknown ok_method: {}', course.ok_method)
        raise ValueError(f'Unknown ok_method: {course.ok_method}')

    is_ok = perc_ok >= course.ok_threshold_perc
    if course.short_name == 'dl_autumn_2022':
        is_ok = course_score_sum >= 5.5

    is_ok = is_ok and (sum(final_results) > 0)  # TODO: one final only ok

    if student_course.score < course_score_sum_with_deadline:
        student_course.score = course_score_sum_with_deadline
        session.add(student_course)
    if student_course.contests_ok < contests_ok:
        student_course.contests_ok = contests_ok
        session.add(student_course)
    if student_course.contests_ok_percent < contests_ok_percent:
        student_course.contests_ok_percent = contests_ok_percent
        session.add(student_course)
    if student_course.score_percent < score_percent:
        student_course.score_percent = score_percent
        session.add(student_course)
    if not student_course.is_ok_final and is_ok:
        student_course.is_ok_final = is_ok
        session.add(student_course)

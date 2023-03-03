# pylint: disable=too-many-lines
import math

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app import constants
from app.database import models
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
                        'name': level.level_name,
                        'score_need': level.ok_threshold
                        if level.count_method
                        == contest_schemas.LevelCountMethod.ABSOLUTE
                        else math.ceil(
                            level.ok_threshold * contest.score_max / 100
                        ),
                        'is_ok': student_level.is_ok,
                        'include_after_deadline': level.include_after_deadline,
                    }
                    for level, student_level in zip(
                        contest_levels, student_contest_levels
                    )
                    if level.level_ok_method
                    == contest_schemas.LevelOkMethod.SCORE_SUM
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
                name=contest.name_format.format(lecture_num=contest.lecture),
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

    logger.info(
        'Student {} has course result',
        student.contest_login,
    )

    return CourseResults(
        name=course.name,
        contests=contests,
        score_sum=student_course.score,
        score_sum_no_deadline=student_course.score_no_deadline,
        score_max=course.score_max,
        is_ok=student_course.is_ok,
        is_ok_final=student_course.is_ok_final,
        perc_ok=0,  # TODO
        str_need=f'Набрано баллов: {student_course.score}/{course.score_max}'
        if course_schemas.LevelOkMethod.SCORE_SUM
        in set(map(lambda x: x.level_ok_method, course_levels))
        else '',
        course_levels=[
            CourseLevelResults(
                name=level.level_name,
                is_ok=sc_level.is_ok,
            )
            for level, sc_level in zip(course_levels, student_course_levels)
        ],
    )


async def update_student_course_results(  # pylint: disable=too-many-statements,too-many-arguments
    student: Student,
    course: Course,
    course_levels: list[CourseLevels],
    student_course: StudentCourse,
    student_course_levels: list[StudentCourseLevels],
    base_logger: 'loguru.Logger',
    session: AsyncSession,
) -> None:
    for (
        contest,
        student_contest,
    ) in await contest_utils.get_contests_with_relations(
        session,
        course.id,
        student.id,
    ):
        logger = base_logger.bind(
            contest={
                'id': contest.id,
                'yandex_contest_id': contest.yandex_contest_id,
            }
        )
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

        await update_student_contest_levels_results(
            student,
            student_course,
            contest,
            student_contest,
            contest_levels,
            student_contest_levels,
            logger=logger,
            session=session,
        )

        student_course.score_percent = round(
            100 * student_course.score / course.score_max, 4
        )
        student_course.contests_ok_percent = round(
            100 * student_course.contests_ok / course.contest_count, 4
        )

        await update_student_course_levels_results(
            student,
            student_course,
            course_levels,
            student_course_levels,
            logger=logger,
            session=session,
        )

        session.add(student_course)


async def update_student_contest_levels_results(  # noqa: C901  # pylint: disable=too-many-arguments,too-many-branches, too-many-statements
    student: models.Student,
    student_course: models.StudentCourse,
    contest: models.Contest,
    student_contest: models.StudentContest,
    contest_levels: list[models.ContestLevels],
    student_contest_levels: list[models.StudentContestLevels],
    logger: 'loguru.Logger',
    session: AsyncSession,
) -> None:
    diffs = {}
    contests_ok_diff = 0
    for (  # pylint: disable=too-many-nested-blocks
        contest_level,
        student_contest_level,
    ) in zip(contest_levels, student_contest_levels):
        if student_contest_level.is_ok:
            continue
        diffs[contest_level.level_name] = {
            'old': student_contest_level.is_ok,
            'new': None,
        }
        if (
            contest_level.level_ok_method
            == contest_schemas.LevelOkMethod.TASKS_COUNT
        ):
            if (
                contest_level.count_method
                == contest_schemas.LevelCountMethod.ABSOLUTE
            ):
                if (  # pylint: disable=no-else-raise  # TODO: remove after implement
                    contest_level.include_after_deadline
                ):
                    raise NotImplementedError(
                        f'Not implemented for '
                        f'{contest_schemas.LevelOkMethod.TASKS_COUNT} '
                        f'{contest_schemas.LevelCountMethod.ABSOLUTE} '
                        f'include_after_deadline'
                    )  # TODO
                else:
                    student_contest_level.is_ok = (
                        student_contest.tasks_done
                        >= contest_level.ok_threshold
                    )
            elif (
                contest_level.count_method
                == contest_schemas.LevelCountMethod.PERCENT
            ):
                if (  # pylint: disable=no-else-raise  # TODO: remove after implement
                    contest_level.include_after_deadline
                ):
                    raise NotImplementedError(
                        f'Not implemented for '
                        f'{contest_schemas.LevelOkMethod.TASKS_COUNT} '
                        f'{contest_schemas.LevelCountMethod.PERCENT} '
                        f'include_after_deadline'
                    )  # TODO
                else:
                    student_contest_level.is_ok = (
                        100 * student_contest.tasks_done / contest.tasks_count
                    ) >= contest_level.ok_threshold
            else:
                raise RuntimeError(
                    f'Contest level count method '
                    f'{contest_level.count_method} not found'
                )
        elif (
            contest_level.level_ok_method
            == contest_schemas.LevelOkMethod.SCORE_SUM
        ):
            if (
                contest_level.count_method
                == contest_schemas.LevelCountMethod.ABSOLUTE
            ):
                if contest_level.include_after_deadline:
                    student_contest_level.is_ok = (
                        student_contest.score_no_deadline
                        >= contest_level.ok_threshold
                    )
                else:
                    student_contest_level.is_ok = (
                        student_contest.score >= contest_level.ok_threshold
                    )
            elif (
                contest_level.count_method
                == contest_schemas.LevelCountMethod.PERCENT
            ):
                if contest_level.include_after_deadline:
                    student_contest_level.is_ok = (
                        100
                        * student_contest.score_no_deadline
                        / contest.score_max
                    ) >= contest_level.ok_threshold
                else:
                    student_contest_level.is_ok = (
                        100 * student_contest.score / contest.score_max
                    ) >= contest_level.ok_threshold
            else:
                raise RuntimeError(
                    f'Contest level count method '
                    f'{contest_level.count_method} not found'
                )
        else:
            raise RuntimeError(
                f'Contest level ok method '
                f'{contest_level.level_ok_method} not found'
            )
        diffs[contest_level.level_name]['new'] = student_contest_level.is_ok
        if contest_level.level_name == 'Зачет автоматом':  # TODO: remove?
            contests_ok_diff = (
                0 if student_contest.is_ok else student_contest_level.is_ok
            )
            student_contest.is_ok = (
                student_contest.is_ok or student_contest_level.is_ok
            )
        elif contest_level.level_name == 'Допуск к зачету':
            student_contest.is_ok_no_deadline = (
                student_contest.is_ok_no_deadline
                or student_contest_level.is_ok
            )
        session.add(student_contest_level)

    student_course.contests_ok += contests_ok_diff
    session.add(student_contest)
    session.add(student_course)

    updated_levels = [
        key for key, value in diffs.items() if value['old'] != value['new']
    ]
    if updated_levels:
        logger.info(
            'Student {} updated contest levels: {}',
            student.contest_login,
            updated_levels,
        )


async def update_student_course_levels_results(  # pylint: disable=too-many-arguments
    student: models.Student,
    student_course: StudentCourse,
    course_levels: list[CourseLevels],
    student_course_levels: list[StudentCourseLevels],
    logger: 'loguru.Logger',
    session: AsyncSession,
) -> None:
    diffs = {}
    for course_level, student_course_level in zip(
        course_levels, student_course_levels
    ):
        if student_course_level.is_ok:
            continue
        diffs[course_level.level_name] = {
            'old': student_course_level.is_ok,
            'new': None,
        }
        if (
            course_level.level_ok_method
            == course_schemas.LevelOkMethod.CONTESTS_OK
        ):
            if (
                course_level.count_method
                == course_schemas.LevelCountMethod.ABSOLUTE
            ):
                student_course_level.is_ok = (
                    student_course.contests_ok >= course_level.ok_threshold
                )
            elif (
                course_level.count_method
                == course_schemas.LevelCountMethod.PERCENT
            ):
                student_course_level.is_ok = (
                    student_course.contests_ok_percent
                    >= course_level.ok_threshold
                )
            else:
                raise RuntimeError(
                    f'Course level count method '
                    f'{course_level.count_method} not found'
                )
        elif (
            course_level.level_ok_method
            == course_schemas.LevelOkMethod.SCORE_SUM
        ):
            if (
                course_level.count_method
                == course_schemas.LevelCountMethod.ABSOLUTE
            ):
                student_course_level.is_ok = (
                    student_course.score >= course_level.ok_threshold
                )
            elif (
                course_level.count_method
                == course_schemas.LevelCountMethod.PERCENT
            ):
                student_course_level.is_ok = (
                    student_course.score_percent >= course_level.ok_threshold
                )
            else:
                raise RuntimeError(
                    f'Course level count method '
                    f'{course_level.count_method} not found'
                )
        else:
            raise RuntimeError(
                f'Course level ok method '
                f'{course_level.level_ok_method} not found'
            )
        diffs[course_level.level_name]['new'] = student_course_level.is_ok
        if course_level.level_name == 'Зачет автоматом':  # TODO: remove?
            student_course.is_ok = (
                student_course.is_ok or student_course_level.is_ok
            )
        session.add(student_course_level)

    session.add(student_course)

    updated_levels = [
        key for key, value in diffs.items() if value['old'] != value['new']
    ]
    if updated_levels:
        logger.info(
            'Student {} updated course levels: {}',
            student.contest_login,
            updated_levels,
        )


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

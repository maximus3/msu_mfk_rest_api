# pylint: disable=too-many-lines
import datetime
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
    student_course_contest_data: list[
        tuple[
            models.Contest,
            models.StudentCourse,
            list[models.ContestLevels],
            list[models.StudentContestLevels],
        ]
    ],
    logger: 'loguru.Logger',
) -> CourseResults:
    contests = []

    for (
        contest,
        student_contest,
        contest_levels,
        student_contest_levels,
    ) in student_course_contest_data:
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
                deadline=contest.deadline.strftime(
                    constants.dt_format,
                ),
            )
        )

    logger.info(
        'Student {} has course result',
        student.contest_login,
    )

    level_ok_methods = set()
    for x in course_levels:
        level_ok_methods |= set(
            map(
                lambda y: y.level_ok_method,
                course_schemas.LevelInfo(data=x.level_info['data']).data,
            )
        )
    real_score_sum = sum(
        map(
            lambda x: x.score_max if not x.is_final and x.is_necessary else 0,
            contests,
        )
    )
    level_names = list(map(lambda level: level.level_name, course_levels))
    course_levels_front = []
    was_ok_zachet = False
    for level_name in [
        'Досрочный зачет',
        'Зачет автоматом',
        'Зачет',
        'Сертификат',
    ]:
        if level_name not in level_names:
            continue
        idx = level_names.index(level_name)
        if student_course_levels[idx].is_ok > student_course.is_ok:
            raise RuntimeError(
                f'Student {student.contest_login} have '
                f'difference in course results and course levels'
            )
        course_level_results = CourseLevelResults(
            name=course_levels[idx].level_name,
            is_ok=student_course_levels[idx].is_ok,
        )
        if level_name == 'Сертификат':
            course_levels_front.append(course_level_results)
            continue
        if level_name == 'Досрочный зачет' and student_course.allow_early_exam:
            course_levels_front.append(course_level_results)
            was_ok_zachet = True
            continue
        if was_ok_zachet:
            continue
        course_levels_front.append(course_level_results)
        was_ok_zachet = True

    return CourseResults(
        name=course.name,
        contests=contests,
        score_sum=student_course.score,
        score_sum_no_deadline=student_course.score_no_deadline,
        score_max=real_score_sum,
        is_ok=student_course.is_ok,
        is_ok_final=student_course.is_ok_final,
        early_exam=student_course.allow_early_exam,
        perc_ok=0,  # TODO
        str_need=f'Набрано баллов: {student_course.score}/{real_score_sum}'
        if course_schemas.LevelOkMethod.SCORE_SUM in level_ok_methods
        else '',
        course_levels=course_levels_front,
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
    contests_data_raw = await contest_utils.get_contests_with_relations(
        session,
        course.id,
        student.id,
    )
    contests_data_all = []
    for (
        contest,
        student_contest,
    ) in contests_data_raw:
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
        contests_data_all.append(
            (contest, student_contest, contest_levels, student_contest_levels)
        )
    for (
        contest,
        student_contest,
        contest_levels,
        student_contest_levels,
    ) in contests_data_all:
        logger = base_logger.bind(
            contest={
                'id': contest.id,
                'yandex_contest_id': contest.yandex_contest_id,
            }
        )
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
        contests_data_all,
        logger=base_logger,
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
        if contest_level.level_name in (
            'Зачет автоматом',
            'Зачет',
        ):  # TODO: remove?
            contests_ok_diff = (
                0 if student_contest.is_ok else student_contest_level.is_ok
            )
            student_contest.is_ok = (
                student_contest.is_ok or student_contest_level.is_ok
            )
            student_contest.is_ok_no_deadline = (
                student_contest.is_ok_no_deadline or student_contest.is_ok
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


async def update_student_course_levels_results(  # pylint: disable=too-many-arguments,too-many-nested-blocks,too-many-branches,too-many-statements  # noqa: C901
    student: models.Student,
    student_course: StudentCourse,
    course_levels: list[CourseLevels],
    student_course_levels: list[StudentCourseLevels],
    contests_data_all: list[
        tuple[
            models.Contest,
            models.StudentContest,
            list[models.ContestLevels],
            list[models.StudentContestLevels],
        ]
    ],
    logger: 'loguru.Logger',
    session: AsyncSession,
) -> None:
    diffs = {}
    for course_level, student_course_level in zip(
        course_levels, student_course_levels
    ):
        logger.info(
            'Start matching course_level {} for student {}',
            course_level.level_name,
            student.contest_login,
        )
        if (
            course_level.result_update_end
            and datetime.datetime.now() > course_level.result_update_end
        ):
            logger.info(
                'Results not updated for course '
                'level {} because of result_update_end {} > {}',
                course_level.level_name,
                datetime.datetime.now(),
                course_level.result_update_end,
            )
            continue
        if student_course.is_ok:
            continue
        diffs[course_level.level_name] = {
            'old': student_course_level.is_ok,
            'new': None,
        }
        if not course_level.level_info:
            logger.warning('level_info is empty, skipping')
            continue
        if not student_course_level.is_ok:
            is_ok = True
            level_info = course_schemas.LevelInfo(
                data=course_level.level_info['data']
            )
            count_levels = len(level_info.data)
            for level_elem in level_info.data:
                count_levels += 1
                if (
                    level_elem.level_ok_method
                    == course_schemas.LevelOkMethod.CONTESTS_OK
                ):
                    count_ok_by_level_contests = 0
                    count_all_contests = 0
                    for (
                        contest,
                        _,
                        contest_levels,
                        student_contest_levels,
                    ) in contests_data_all:
                        if set(level_elem.tags) <= set(contest.tags):
                            count_all_contests += 1
                            contest_level_names = [
                                contest_level.level_name
                                for contest_level in contest_levels
                            ]
                            if (
                                level_elem.contest_ok_level_name
                                not in contest_level_names
                            ):
                                logger.error(
                                    'Contest {} has no level {}',
                                    contest.yandex_contest_id,
                                    level_elem.contest_ok_level_name,
                                )
                                continue
                            index_of_level_name = contest_level_names.index(
                                level_elem.contest_ok_level_name
                            )
                            count_ok_by_level_contests += (
                                student_contest_levels[
                                    index_of_level_name
                                ].is_ok
                            )
                        else:
                            logger.info(
                                'Contest {} not included in matching '
                                'because of tags level_elem {} not in '
                                'contest tags {}',
                                contest.yandex_contest_id,
                                level_elem.tags,
                                contest.tags,
                            )
                    logger.info(
                        'Matching student {} for level_elem {}. '
                        'count_ok_by_level_contests={}, '
                        'count_all_contests={}',
                        student.contest_login,
                        level_elem,
                        count_ok_by_level_contests,
                        count_all_contests,
                    )
                    if (
                        level_elem.count_method
                        == course_schemas.LevelCountMethod.ABSOLUTE
                    ):
                        is_ok = (
                            is_ok
                            and count_ok_by_level_contests
                            >= level_elem.ok_threshold
                        )
                    elif (
                        level_elem.count_method
                        == course_schemas.LevelCountMethod.PERCENT
                    ):
                        is_ok = (
                            is_ok
                            and round(
                                100
                                * count_ok_by_level_contests
                                / count_all_contests,
                                4,
                            )
                            >= level_elem.ok_threshold
                        )
                    else:
                        raise RuntimeError(
                            f'Course level count method '
                            f'{level_elem.count_method} not found'
                        )
                elif (
                    level_elem.level_ok_method
                    == course_schemas.LevelOkMethod.SCORE_SUM
                ):
                    sum_score_by_tag_contests = 0
                    sum_score_all_tag_contests = 0
                    for (
                        contest,
                        student_contest,
                        contest_levels,
                        student_contest_levels,
                    ) in contests_data_all:
                        if set(level_elem.tags) <= set(contest.tags):
                            sum_score_by_tag_contests += student_contest.score
                            sum_score_all_tag_contests += contest.score_max
                        else:
                            logger.info(
                                'Contest {} not included in matching '
                                'because of tags level_elem {} not in '
                                'contest tags {}',
                                contest.yandex_contest_id,
                                level_elem.tags,
                                contest.tags,
                            )
                    logger.info(
                        'Matching student {} for level_elem {}. '
                        'sum_score_by_tag_contests={}, '
                        'sum_score_all_tag_contests={}',
                        student.contest_login,
                        level_elem,
                        sum_score_by_tag_contests,
                        sum_score_all_tag_contests,
                    )
                    if (
                        level_elem.count_method
                        == course_schemas.LevelCountMethod.ABSOLUTE
                    ):
                        is_ok = (
                            is_ok
                            and sum_score_by_tag_contests
                            >= level_elem.ok_threshold
                        )
                    elif (
                        level_elem.count_method
                        == course_schemas.LevelCountMethod.PERCENT
                    ):
                        is_ok = (
                            is_ok
                            and round(
                                100
                                * sum_score_by_tag_contests
                                / sum_score_all_tag_contests,
                                4,
                            )
                            >= level_elem.ok_threshold
                        )
                    else:
                        raise RuntimeError(
                            f'Course level count method '
                            f'{level_elem.count_method} not found'
                        )
                else:
                    raise RuntimeError(
                        f'Course level ok method '
                        f'{level_elem.level_ok_method} not found'
                    )
            student_course_level.is_ok = is_ok and (count_levels > 0)
            diffs[course_level.level_name]['new'] = student_course_level.is_ok
        if course_level.level_name in (
            'Зачет автоматом',
            'Зачет',
            'Досрочный зачет',
        ):  # TODO: remove?
            was = student_course.is_ok
            student_course.is_ok = (
                student_course.is_ok or student_course_level.is_ok
            )
            if was != student_course.is_ok:
                logger.info(
                    'Student {} updated course result is ok to {}',
                    student.contest_login,
                    student_course.is_ok,
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

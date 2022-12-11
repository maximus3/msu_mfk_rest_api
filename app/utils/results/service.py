import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Course, Student
from app.schemas import ContestResults, CourseResults
from app.utils.common import get_datetime_msk_tz
from app.utils.contest import get_contests_with_relations


async def get_student_course_results(
    student: Student, course: Course, session: AsyncSession
) -> CourseResults:
    logger = logging.getLogger(__name__)

    contests = []
    course_score_sum = 0
    course_score_max = 0

    for contest, student_contest in sorted(
        await get_contests_with_relations(
            session,
            course.id,
            student.id,
        ),
        key=lambda x: x[0].lecture,
    ):
        course_score_sum += student_contest.score
        course_score_max += contest.score_max

        contests.append(
            ContestResults(
                link=contest.link,
                tasks_count=contest.tasks_count,
                score_max=contest.score_max,
                levels_count=contest.levels['count'] if contest.levels else 0,
                levels=sorted(
                    contest.levels['levels'],
                    key=lambda level: level['score_need'],
                )
                if contest.levels
                else [],
                levels_ok=[
                    (student_contest.score or 0) >= level.score_need
                    for level in sorted(
                        contest.levels['levels'],
                        key=lambda level: level['score_need'],
                    )
                ]
                if contest.levels
                else [],
                lecture=contest.lecture,
                tasks_done=student_contest.tasks_done or 0,
                score=student_contest.score or 0,
                is_ok=student_contest.is_ok,
                is_necessary=contest.is_necessary,
                updated_at=get_datetime_msk_tz(
                    student_contest.dt_updated
                ).strftime(
                    '%Y-%m-%d %H:%M:%S',
                ),
                deadline=get_datetime_msk_tz(contest.deadline,).strftime(
                    '%Y-%m-%d %H:%M:%S',
                ),
            )
        )

    count_necessary_contests = sum(
        1 for contest in contests if contest.is_necessary
    )
    if course.ok_method == 'contests_ok':
        perc_ok = (
            100
            * sum(
                contest.is_ok
                for contest in filter(lambda x: x.is_necessary, contests)
            )
            / count_necessary_contests
        )
    elif course.ok_method == 'score_sum':
        perc_ok = 100 * course_score_sum / course_score_max
    else:
        logger.error('Unknown ok_method: %s', course.ok_method)
        raise ValueError(f'Unknown ok_method: {course.ok_method}')

    is_ok = perc_ok >= course.ok_threshold_perc

    return CourseResults(
        name=course.name,
        contests=contests,
        score_sum=course_score_sum,
        score_max=course_score_max,
        is_ok=is_ok,
        perc_ok=int(perc_ok),
    )

# pylint: disable=duplicate-code,too-many-lines

import traceback
import uuid

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_helper import send
from app.bot_helper.send import send_message
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
from app.schemas import ContestSubmissionFull, Levels
from app.utils.contest import (
    add_student_contest_relation,
    get_author_id,
    get_best_submissions,
    get_contests,
    get_student_contest_relation,
)
from app.utils.contest.database import get_ok_author_ids
from app.utils.course import get_all_active_courses
from app.utils.scheduler import write_sql_tqdm
from app.utils.student import get_students_by_course_with_department


async def check_student_contest_relation(
    student: Student,
    contest: Contest,
    logger: 'loguru.Logger',
    session: AsyncSession | None = None,
) -> StudentContest:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await check_student_contest_relation(
                student,
                contest,
                logger,
                session,
            )
    student_contest = await get_student_contest_relation(
        session, student.id, contest.id
    )

    if student_contest is None:
        logger.warning(
            'Student {} has no relation with contest {}',
            student.contest_login,
            contest.id,
        )
        student_contest = await add_student_contest_relation(
            session,
            student.id,
            contest.id,
            contest.course_id,
            await get_author_id(
                student.contest_login, contest.yandex_contest_id, logger=logger
            ),
        )
        session.add(student_contest)
    elif student_contest.author_id is None:
        logger.info(
            'Student {} has no author id in contest {}',
            student.contest_login,
            contest.id,
        )
        student_contest.author_id = await get_author_id(
            student.contest_login, contest.yandex_contest_id, logger=logger
        )
        session.add(student_contest)
    return student_contest


async def update_student_contest_relation(  # pylint: disable=too-many-arguments
    student: Student,
    contest: Contest,
    student_contest: StudentContest,
    student_tasks_done: int,
    student_score: float,
    student_score_no_deadline: float,
    is_ok: bool,
    logger: 'loguru.Logger',
    session: AsyncSession | None = None,
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
                session,
                logger,
            )
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
    if not changes:
        logger.info(
            'Student {} has no changes in contest {}',
            student.contest_login,
            contest.id,
        )


async def process_student(  # pylint: disable=too-many-arguments
    student: Student,
    student_course: StudentCourse,
    department: Department,
    contest: Contest,
    course: Course,
    results: list[ContestSubmissionFull],
    contest_levels: Levels | None,
    course_score_sum: float,
    logger: 'loguru.Logger',
    session: AsyncSession | None = None,
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
                results,
                contest_levels,
                course_score_sum,
                session=session,
                logger=logger,
            )
    student_contest = await check_student_contest_relation(
        student, contest, session=session, logger=logger
    )
    if student_contest.is_ok:
        return
    student_tasks_done = sum(
        True
        for submission in results
        if submission.authorId == student_contest.author_id
    )
    student_score = round(
        sum(
            submission.finalScore
            for submission in results
            if submission.authorId == student_contest.author_id
        ),
        4,
    )  # TODO: magic constant
    student_score_no_deadline = round(
        sum(
            submission.noDeadlineScore
            for submission in results
            if submission.authorId == student_contest.author_id
        ),
        4,
    )  # TODO: magic constant
    is_ok = student_tasks_done == contest.tasks_count
    logger.info(
        'Student: {}, tasks done: {}, score: {}, is ok: {}',
        student.contest_login,
        student_tasks_done,
        student_score,
        is_ok,
    )
    if contest_levels and contest_levels.count > 0:
        is_ok = student_score >= min(
            level.score_need for level in contest_levels.levels
        )

    if student_contest.score == contest.score_max:
        logger.debug(
            'Student {} has already max score in contest {}',
            student.contest_login,
            contest.id,
        )
        return
    await update_student_contest_relation(
        student,
        contest,
        student_contest,
        student_tasks_done,
        student_score,
        student_score_no_deadline,
        is_ok,
        logger=logger,
        session=session,
    )


async def process_contest(  # pylint: disable=too-many-arguments
    students_sc_departments: list[tuple[Student, StudentCourse, Department]],
    results: list[ContestSubmissionFull],
    contest: Contest,
    course: Course,
    course_score_sum: float,
    logger: 'loguru.Logger',
    session: AsyncSession | None = None,
) -> None:
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
        await process_student(
            student,
            student_course,
            department,
            contest,
            course,
            results,
            contest_levels,
            course_score_sum,
            logger=logger,
            session=session,
        )


async def update_course_results(
    course: Course,
    logger: 'loguru.Logger',
) -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        contests = await get_contests(session, course.id)
        students_sc_departments = await get_students_by_course_with_department(
            session, course.id
        )
    is_all_results_ok = True
    contests.sort(key=lambda x: x.lecture)
    course_score_sum = 0
    async for contest in tqdm(
        contests,
        name='contest_results_contests',
        logger=logger,
        sql_write_func=write_sql_tqdm,
    ):
        logger.info('Contest: {}', contest)
        course_score_sum += contest.score_max
        async with SessionManager().create_async_session() as session:
            ok_authors_ids = set(
                await get_ok_author_ids(session, course.id, contest.id)
            )
        results, is_all_results = await get_best_submissions(
            contest,
            logger=logger,
            zero_is_ok=course.short_name
            in ['ml_autumn_2022', 'da_autumn_2022'],  # TODO: magic constant
            ok_authors_ids=ok_authors_ids,
        )
        is_all_results_ok = is_all_results_ok and is_all_results
        await process_contest(
            students_sc_departments,
            results,
            contest,
            course,
            course_score_sum,
            logger=logger,
        )
    if not is_all_results_ok:
        logger.error('Not all results ok')
        raise RuntimeError('Not all results ok')


async def job() -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        courses = await get_all_active_courses(session)
    logger = loguru.logger.bind(uuid=uuid.uuid4().hex)
    async for course in tqdm(
        courses,
        name='contest_results_courses',
        logger=logger,
        sql_write_func=write_sql_tqdm,
    ):
        logger.info('Course: {}', course)
        try:
            await update_course_results(course, logger)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                'Error while updating course results for {}: {}',
                course.name,
                exc,
            )
            try:
                await send.send_traceback_message(
                    f'Error while updating course '
                    f'results for {course.name}: {exc}',
                    code=traceback.format_exc(),
                )
            except Exception as send_exc:  # pylint: disable=broad-except
                logger.exception(
                    'Error while sending error message: {}', send_exc
                )
            continue

    await send_message(
        'Results updated',
        level='info',
    )


job_info = {
    'func': job,
    'trigger': 'interval',
    'hours': 1,
    'name': 'contest_results',
}

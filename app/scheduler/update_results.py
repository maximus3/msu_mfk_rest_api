# pylint: disable=too-many-lines

import traceback
import uuid

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_helper import send
from app.database import models
from app.database.connection import SessionManager
from app.m3tqdm import tqdm
from app.schemas import contest as contest_schemas
from app.schemas import course as course_schemas
from app.schemas import scheduler as scheduler_schemas
from app.utils import contest as contest_utils
from app.utils import course as course_utils
from app.utils import student as student_utils
from app.utils import submission as submission_utils
from app.utils import task as task_utils


async def job() -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        courses = await course_utils.get_all_active_courses(session)
    base_logger = loguru.logger.bind(uuid=uuid.uuid4().hex)
    async for course in tqdm(
        courses,
        name=job_info.name + '-courses',
    ):
        logger = base_logger.bind(
            course={'id': course.id, 'short_name': course.short_name}
        )
        logger.info('Course: {}', course)
        try:
            await update_course_results(course, logger)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                'Error while updating course results for {}: {}',
                course.short_name,
                exc,
            )
            await send.send_traceback_message_safe(
                logger=logger,
                message=f'Error while updating course '
                f'results for {course.short_name}: {exc}',
                code=traceback.format_exc(),
            )
            continue

    await send.send_message(
        'Results updated',
        level='info',
    )


async def update_course_results(
    course: models.Course,
    base_logger: 'loguru.Logger',
) -> None:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        contests = await contest_utils.get_contests(session, course.id)
        students_sc_departments = (
            await student_utils.get_students_by_course_with_department(
                session, course.id
            )
        )
    contests.sort(key=lambda x: x.lecture)
    course_score_sum = sum(contest.score_max for contest in contests)
    if course.score_max != course_score_sum:
        raise RuntimeError(
            f'Course {course.id} has {course.score_max} '
            f'score max, but got {course_score_sum} score sum'
        )
    if course.contest_count != len(contests):
        raise RuntimeError(
            f'Course {course.id} has {course.contest_count} '
            f'contest count, but got {len(contests)} contests'
        )
    async for contest in tqdm(
        contests,
        name=job_info.name + '-contests',
    ):
        logger = base_logger.bind(
            contest={
                'id': contest.id,
                'yandex_contest_id': contest.yandex_contest_id,
            }
        )
        logger.info('Contest: {}', contest)
        await check_student_contest_relations(
            contest,
            students_sc_departments,
            base_logger=logger,
        )
        async with SessionManager().create_async_session() as session:
            last_updated_submission = (
                await task_utils.get_last_updated_submission(
                    session, contest.id
                )
                or -1
            )
        submissions = await contest_utils.get_new_submissions(
            contest, last_updated_submission, logger=logger
        )
        await process_submissions(
            course,
            contest,
            submissions,
            base_logger=logger,
        )


async def check_student_contest_relations(
    contest: models.Contest,
    students_sc_departments: list[
        tuple[models.Student, models.StudentCourse, models.Department]
    ],
    base_logger: 'loguru.Logger',
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await check_student_contest_relations(
                contest,
                students_sc_departments,
                base_logger=base_logger,
                session=session,
            )
    async for student, _, _ in tqdm(
        students_sc_departments,
        name=job_info.name + '-check_student_contest_relations',
    ):
        logger = base_logger.bind(
            student={'id': student.id, 'contest_login': student.contest_login}
        )
        student_contest = await contest_utils.get_student_contest_relation(
            session, student.id, contest.id
        )

        if student_contest is None:
            logger.info(
                'Student {} has no relation with contest {}, creating',
                student.id,
                contest.id,
            )
            student_contest = await contest_utils.add_student_contest_relation(
                session,
                student.id,
                contest.id,
                contest.course_id,
                await contest_utils.get_author_id(
                    student.contest_login,
                    contest.yandex_contest_id,
                    logger=logger,
                ),
            )
            session.add(student_contest)
        elif student_contest.author_id is None:
            logger.info(
                'Student {} has no author id in contest {}, adding',
                student.id,
                contest.id,
            )
            student_contest.author_id = await contest_utils.get_author_id(
                student.contest_login, contest.yandex_contest_id, logger=logger
            )
            session.add(student_contest)


async def process_submissions(
    course: models.Course,
    contest: models.Contest,
    submissions: list[contest_schemas.ContestSubmissionFull],
    base_logger: 'loguru.Logger',
) -> None:
    for submission in submissions:
        async with SessionManager().create_async_session() as session:
            task = await task_utils.get_task(
                session, contest.id, submission.problemId
            )
        if task is None:
            raise RuntimeError(
                f'Task {submission.problemId} not '
                f'found for contest {contest.id}'
            )
        await process_submission(
            course,
            contest,
            task,
            submission,
            base_logger=base_logger,
        )


async def process_submission(  # noqa: C901 # pylint: disable=too-many-arguments,too-many-branches,too-many-statements # TODO
    course: models.Course,
    contest: models.Contest,
    task: models.Task,
    submission: contest_schemas.ContestSubmissionFull,
    base_logger: 'loguru.Logger',
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await process_submission(
                course,
                contest,
                task,
                submission,
                base_logger=base_logger,
                session=session,
            )
    (
        student,
        student_course,
        student_contest,
    ) = await student_utils.get_or_create_all_student_models(
        session,
        course.id,
        contest.id,
        author_id=submission.authorId,
    )
    logger = base_logger.bind(
        student={'id': student.id, 'contest_login': student.contest_login},
        task={'id': task.id, 'yandex_task_id': task.yandex_task_id},
    )
    student_task = await check_student_task_relation(
        student,
        contest,
        course,
        task,
        logger,
        session,
    )
    submission_model = await submission_utils.get_submission(
        session,
        submission.id,
    )
    if submission_model is not None:
        logger.warning(
            'Submission {} already in database (id={})',
            submission.id,
            submission_model.id,
        )
        await send.send_message_safe(
            logger,
            message=f'Submission {submission.id} already '
            f'in database (id={submission_model.id})',
            level='warning',
        )
    submission_model = await submission_utils.add_submission(
        session,
        student,
        contest,
        course,
        task,
        student_task,
        submission,
    )
    await session.flush()
    if (  # pylint: disable=too-many-nested-blocks  # TODO
        submission_model.final_score > student_task.final_score
        or submission_model.no_deadline_score > student_task.no_deadline_score
    ):  # TODO: check block other transactions
        is_done_submission = submission_model.final_score == task.score_max

        score_diff = submission_model.final_score - student_task.final_score
        no_deadline_score_diff = (
            submission_model.no_deadline_score - student_task.no_deadline_score
        )
        is_done_diff = 0 if student_task.is_done else is_done_submission

        student_task.best_submission_id = submission_model.id
        student_task.final_score = submission_model.final_score
        student_task.no_deadline_score = submission_model.no_deadline_score
        student_task.is_done = student_task.is_done or is_done_submission

        student_contest.score += score_diff
        student_contest.score_no_deadline += no_deadline_score_diff
        student_contest.tasks_done += is_done_diff

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
        contests_ok_diff = 0
        for contest_level, student_contest_level in zip(
            contest_levels, student_contest_levels
        ):
            if student_contest_level.is_ok:
                continue
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
                            100
                            * student_contest.tasks_done
                            / contest.tasks_count
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
            if contest_level.level_name == 'Зачет автоматом':  # TODO: remove
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

        student_course.score += score_diff
        student_course.contests_ok += contests_ok_diff
        student_course.score_percent = (
            100 * student_course.score / course.score_max
        )
        student_course.contests_ok_percent = (
            100 * student_course.contests_ok / course.contest_count
        )

        course_levels = await course_utils.get_course_levels(
            session, course.id
        )  # TODO: add types FINAL, NECESSARY contests for levels
        course_levels.sort(key=lambda x: (x.count_method, x.ok_threshold))
        student_course_levels = [
            await course_utils.get_or_create_student_course_level(
                session, student.id, course.id, level.id
            )
            for level in course_levels
        ]
        for course_level, student_course_level in zip(
            course_levels, student_course_levels
        ):
            if student_course_level.is_ok:
                continue
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
                        student_course.score_percent
                        >= course_level.ok_threshold
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
            if course_level.level_name == 'Зачет автоматом':  # TODO: remove
                student_course.is_ok = (
                    student_course.is_ok or student_course_level.is_ok
                )


async def check_student_task_relation(  # pylint: disable=too-many-arguments
    student: models.Student,
    contest: models.Contest,
    course: models.Course,
    task: models.Task,
    logger: 'loguru.Logger',
    session: AsyncSession | None = None,
) -> models.StudentTask:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await check_student_task_relation(
                student,
                contest,
                course,
                task,
                logger,
                session,
            )
    student_task = await task_utils.get_student_task_relation(
        session, student.id, task.id
    )

    if student_task is None:
        logger.info(
            'Student {} has no relation with task {}, creating',
            student.id,
            task.id,
        )
        student_task = await task_utils.add_student_task_relation(
            session,
            student,
            contest,
            course,
            task,
        )
        session.add(student_task)
    return student_task


job_info = scheduler_schemas.JobInfo(
    func=job, name='update_results', trigger='interval', hours=1
)

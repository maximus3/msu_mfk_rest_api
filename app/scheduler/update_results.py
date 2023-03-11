# pylint: disable=too-many-lines
import collections
import pathlib
import traceback
from datetime import datetime

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app import constants
from app.bot_helper import send
from app.database import models
from app.database.connection import SessionManager
from app.schemas import contest as contest_schemas
from app.schemas import course as course_schemas
from app.utils import contest as contest_utils
from app.utils import course as course_utils
from app.utils import results as results_utils
from app.utils import student as student_utils
from app.utils import submission as submission_utils
from app.utils import task as task_utils


async def job(  # pylint: disable=too-many-statements
    base_logger: 'loguru.Logger', save_csv: bool = True
) -> None:
    SessionManager().refresh()

    try:
        await check_and_update_no_verdict_submissions(base_logger)
    except Exception as exc:  # pylint: disable=broad-except
        base_logger.exception(
            'Error while check_and_update_no_verdict_submissions: {}',
            exc,
        )
        await send.send_traceback_message_safe(
            logger=base_logger,
            message=f'Error while '
            f'check_and_update_no_verdict_submissions: {exc}',
            code=traceback.format_exc(),
        )

    async with SessionManager().create_async_session() as session:
        courses = await course_utils.get_all_active_courses(session)
        levels_by_course = [
            await course_utils.get_course_levels(session, course.id)
            for course in courses
        ]
    base_logger.info(
        'Has {} courses', len(courses)
    )
    filenames = []
    for course, course_levels in zip(courses, levels_by_course):
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

        # dump results
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
        if save_csv:
            await save_to_csv(course_results, filename)
            filenames.append(filename)

    try:
        await send.send_results(filenames)
    except Exception as exc:
        base_logger.error('Error while sending results: {}', exc)
        raise exc
    finally:
        for filename in filenames:
            pathlib.Path(filename).unlink()


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
        course_levels = await course_utils.get_course_levels(
            session, course.id
        )  # TODO: add types FINAL, NECESSARY contests for levels
        course_levels.sort(key=lambda x: (x.count_method, x.ok_threshold))
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
    for contest in contests:
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
            last_updated_submission_model = (
                await submission_utils.get_last_updated_submission(
                    session, contest.id
                )
            )
            last_updated_submission = (
                last_updated_submission_model.run_id
                if last_updated_submission_model
                else -1
            )
            contest_levels = await contest_utils.get_contest_levels(
                session, contest.id
            )
            contest_levels.sort(key=lambda x: (x.count_method, x.ok_threshold))
        submissions = await contest_utils.get_new_submissions(
            contest, last_updated_submission, logger=logger
        )
        submissions.sort(key=lambda x: x.id)
        await process_submissions(
            course,
            course_levels,
            contest,
            contest_levels,
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
    for student, _, _ in students_sc_departments:
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


async def process_submissions(  # pylint: disable=too-many-arguments
    course: models.Course,
    course_levels: list[models.CourseLevels],
    contest: models.Contest,
    contest_levels: list[models.ContestLevels],
    submissions: list[contest_schemas.ContestSubmissionFull],
    base_logger: 'loguru.Logger',
) -> None:
    base_logger.info('Got {} submissions for process', len(submissions))
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
            course_levels,
            contest,
            contest_levels,
            task,
            submission,
            base_logger=base_logger,
        )


async def process_submission(  # noqa: C901 # pylint: disable=too-many-arguments,too-many-branches,too-many-statements # TODO
    course: models.Course,
    course_levels: list[models.CourseLevels],
    contest: models.Contest,
    contest_levels: list[models.ContestLevels],
    task: models.Task,
    submission: contest_schemas.ContestSubmissionFull,
    base_logger: 'loguru.Logger',
    submission_model: models.Submission | None = None,
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await process_submission(
                course,
                course_levels,
                contest,
                contest_levels,
                task,
                submission,
                base_logger=base_logger,
                submission_model=submission_model,
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
    if student is None or student_course is None or student_contest is None:
        logger = base_logger.bind(
            task={'id': task.id, 'yandex_task_id': task.yandex_task_id},
            submission={'id': submission.id, 'author_id': submission.authorId},
        )
        logger.warning(
            'No student with such author id {}: student {}, '
            'student course {}, student contest {}. '
            'Submission {} will not be processed',
            submission.authorId,
            student,
            student_course,
            student_contest,
            submission.id,
        )
        await send.send_message_safe(
            logger=logger,
            message=f'No student with such author id '
            f'{submission.authorId}: student {student}, '
            f'student course {student_course}, '
            f'student contest {student_contest}. '
            f'Submission {submission.id} (https://admin.contest.yandex.ru/'
            f'submissions/{submission.id}/) '
            f'will not be processed',
        )
        return
    logger = base_logger.bind(
        student={'id': student.id, 'contest_login': student.contest_login},
        task={'id': task.id, 'yandex_task_id': task.yandex_task_id},
        submission={'id': submission.id, 'author_id': submission.authorId},
    )
    student_task = await check_student_task_relation(
        student,
        contest,
        course,
        task,
        logger,
        session,
    )
    if submission_model:
        await submission_utils.update_submission(
            session,
            contest,
            task,
            submission,
            submission_model,
        )
    else:
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
            return
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
        or submission_model.score_before_finish
        > student_task.best_score_before_finish
        or submission_model.score_no_deadline
        > student_task.best_score_no_deadline
    ):  # TODO: check block other transactions
        is_done_submission = submission_model.final_score == task.score_max

        final_score_diff = max(
            submission_model.final_score - student_task.final_score, 0
        )
        score_before_finish_diff = max(
            submission_model.score_before_finish
            - student_task.best_score_before_finish,
            0,
        )
        no_deadline_score_diff = max(
            submission_model.score_no_deadline
            - student_task.best_score_no_deadline,
            0,
        )  # TODO: max no need?
        is_done_diff = 0 if student_task.is_done else is_done_submission

        logger.info(
            'Submission {} is new best submission for task {}. '
            'final_score_diff={}, score_before_finish_diff={}'
            'no_deadline_score_diff={}, '
            'is_done_diff={}',
            submission.id,
            task.id,
            final_score_diff,
            score_before_finish_diff,
            no_deadline_score_diff,
            is_done_diff,
        )

        if score_before_finish_diff:
            student_task.best_score_before_finish_submission_id = (
                submission_model.id
            )
        if no_deadline_score_diff:
            student_task.best_score_no_deadline_submission_id = (
                submission_model.id
            )
        student_task.final_score = round(
            student_task.final_score + final_score_diff, 4
        )
        student_task.best_score_before_finish = round(
            student_task.best_score_before_finish + score_before_finish_diff, 4
        )
        student_task.best_score_no_deadline = round(
            student_task.best_score_no_deadline + no_deadline_score_diff, 4
        )
        student_task.is_done = student_task.is_done or is_done_submission

        student_contest.score = round(
            student_contest.score + final_score_diff, 4
        )
        student_contest.score_no_deadline = round(
            student_contest.score_no_deadline + no_deadline_score_diff, 4
        )  # TODO: magic constant
        student_contest.tasks_done += is_done_diff

        student_course.score = round(
            student_course.score + final_score_diff, 4
        )
        student_course.score_no_deadline = round(
            student_course.score_no_deadline + no_deadline_score_diff, 4
        )

        session.add(student_task)
        session.add(student_contest)
        session.add(student_course)


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


async def get_course_results(  # pylint: disable=too-many-statements
    course: models.Course,
    course_levels: list[models.CourseLevels],
    base_logger: 'loguru.Logger',
) -> course_schemas.CourseResultsCSV:
    SessionManager().refresh()
    async with SessionManager().create_async_session() as session:
        students_departments_results = []
        for (
            student,
            student_course,
            department,
        ) in await student_utils.get_students_by_course_with_department(
            session, course.id
        ):
            logger = base_logger.bind(
                student={
                    'id': student.id,
                    'contest_login': student.contest_login,
                }
            )
            student_course_levels = [
                await course_utils.get_or_create_student_course_level(
                    session, student.id, course.id, course_level.id
                )
                for course_level in course_levels
            ]
            await results_utils.update_student_course_results(
                student,
                course,
                course_levels,
                student_course,
                student_course_levels,
                base_logger=logger,
                session=session,
            )
            await session.commit()
            student_course_contest_data = (
                await course_utils.get_student_course_contests_data(
                    session, course.id, student.id
                )
            )
            student_results = await results_utils.get_student_course_results(
                student,
                course,
                course_levels,
                student_course,
                student_course_levels,
                student_course_contest_data,
                logger=logger,
            )
            students_departments_results.append(
                (student, department, student_results)
            )
    course_results = course_schemas.CourseResultsCSV(
        keys=['contest_login', 'fio', 'department'],
        results=collections.defaultdict(dict),
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


async def save_to_csv(
    course_results: course_schemas.CourseResultsCSV, filename: str
) -> None:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(','.join(course_results.keys))
        f.write('\n')
        for data in course_results.results.values():
            for i, key in enumerate(course_results.keys):
                f.write(f'{data.get(key, "")}')
                if i != len(course_results.keys) - 1:
                    f.write(',')
            f.write('\n')


async def check_and_update_no_verdict_submissions(
    base_logger: 'loguru.Logger',
) -> None:
    async with SessionManager().create_async_session() as session:
        no_verdict_submissions = (
            await submission_utils.get_no_verdict_submissions(session)
        )
        for submission in no_verdict_submissions:
            logger = base_logger.bind(
                submission={
                    'id': submission.id,
                    'author_id': submission.author_id,
                },
                course={'id': submission.course_id},
                contest={'id': submission.contest_id},
                task={'id': submission.task_id},
                student={'id': submission.student_id},
            )
            contest = await contest_utils.get_contest_by_id(
                session, submission.contest_id
            )
            yandex_submission = await contest_utils.get_submission_from_yandex(
                contest, submission, logger
            )
            if yandex_submission.verdict == submission.verdict:
                logger.info(
                    'Submission {} has no verdict, skipping',
                    yandex_submission.id,
                )
                continue
            course = await course_utils.get_course_by_id(
                session, submission.course_id
            )
            course_levels = await course_utils.get_course_levels(
                session, course.id
            )
            contest_levels = await contest_utils.get_contest_levels(
                session, contest.id
            )
            task = await task_utils.get_task_by_id(session, submission.task_id)
            await process_submission(
                course,
                course_levels=course_levels,
                contest=contest,
                contest_levels=contest_levels,
                task=task,
                submission=yandex_submission,
                base_logger=logger.bind(
                    course={'id': course.id, 'short_name': course.short_name},
                    contest={
                        'id': contest.id,
                        'yandex_contest_id': contest.yandex_contest_id,
                    },
                ),
                submission_model=submission,
                session=session,
            )

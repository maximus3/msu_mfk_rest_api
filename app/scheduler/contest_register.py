import pathlib
import traceback
import uuid

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_helper import send
from app.database.connection import SessionManager
from app.database.models import Contest, Course, Student
from app.schemas import scheduler as scheduler_schemas
from app.utils.contest import add_student_to_contest, get_contests
from app.utils.course import get_all_active_courses
from app.utils.student import get_students_by_course_with_no_contest


async def register_student(
    session: AsyncSession,
    contest: Contest,
    student: Student,
    logger: 'loguru.Logger',
) -> bool:
    add_ok, message = await add_student_to_contest(
        session,
        contest,
        student,
        logger=logger,
    )
    if not add_ok:
        logger.error(
            'Student {} not registered on contest {}. Reason: {}',
            student.id,
            contest.id,
            message,
        )
        return False
    await session.commit()
    logger.info(
        'Student {} added to contest {}',
        student.id,
        contest.id,
    )
    return True


async def check_students_for_contest_registration(
    session: AsyncSession,
    course: Course,
    base_logger: 'loguru.Logger',
) -> None:
    contests = await get_contests(session, course.id)
    base_logger.info('Course {} has {} contests', course.id, len(contests))
    for contest in contests:
        contest_logger = base_logger.bind(
            contest={
                'id': contest.id,
                'yandex_contest_id': contest.yandex_contest_id,
            }
        )
        contest_logger.info('Contest: {}', contest)
        no_registered_students = await get_students_by_course_with_no_contest(
            session, course.id, contest.id
        )
        contest_logger.info(
            'Contest "{}" has {} no registered students',
            contest.id,
            len(no_registered_students),
        )
        count = 0
        for student in no_registered_students:
            student_logger = contest_logger.bind(
                student={
                    'id': student.id,
                    'contest_login': student.contest_login,
                }
            )
            try:
                count += await register_student(
                    session, contest, student, student_logger
                )
            except Exception as exc:  # pylint: disable=broad-except
                student_logger.exception(
                    'Error while register student {} on contest {}: {}',
                    student.id,
                    contest.id,
                    exc,
                )
                await send.send_traceback_message_safe(
                    logger=student_logger,
                    message=f'Error while register student {student.id} '
                    f'on contest {contest.id}: {exc}',
                    code=traceback.format_exc(),
                )
        contest_logger.info(
            'Successfully added {} students to contest {}',
            count,
            contest.id,
        )


async def job(
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await job(session=session)
    log_id = uuid.uuid4().hex
    log_file_name = f'./logs/scheduler/job-{job_info.name}-{log_id}.log'
    base_logger = loguru.logger.bind(uuid=log_id)
    base_logger.info('Job {} started', job_info.name)
    handler_id = base_logger.add(
        log_file_name,
        serialize=True,
        enqueue=True,
        filter=lambda record: record['extra'].get('uuid') == log_id,
    )
    courses = await get_all_active_courses(session)
    base_logger.info(
        'Has {} courses',
    )
    for course in courses:
        logger = base_logger.bind(
            course={'id': course.id, 'short_name': course.short_name}
        )
        logger.info('Course: {}', course)
        await check_students_for_contest_registration(session, course, logger)
    base_logger.remove(handler_id)
    try:
        await send.send_file(log_file_name, f'job-{job_info.name}-{log_id}')
        pathlib.Path(log_file_name).unlink()
    except Exception as send_exc:  # pylint: disable=broad-except
        base_logger.exception('Error while sending log file: {}', send_exc)
        await send.send_traceback_message_safe(
            logger=base_logger,
            message=f'Error while sending log file: {send_exc}',
            code=traceback.format_exc(),
        )
    base_logger.info('Job {} finished', job_info.name)


job_info = scheduler_schemas.JobInfo(
    **{
        'func': job,
        'trigger': 'interval',
        'minutes': 10,
        'name': 'contest_register',
    }
)

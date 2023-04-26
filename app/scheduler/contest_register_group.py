# pylint: disable=duplicate-code

import traceback
import uuid

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot_helper import send
from app.database import models
from app.database.connection import SessionManager
from app.schemas import contest as contest_schemas
from app.schemas import group as group_schemas
from app.utils import contest as contest_utils
from app.utils import course as course_utils
from app.utils import group as group_utils
from app.utils import student as student_utils


async def job(
    base_logger: 'loguru.Logger',
    session: AsyncSession | None = None,
) -> None:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await job(base_logger=base_logger, session=session)
    courses = await course_utils.get_all_active_courses(session)
    base_logger.info('Has {} courses', len(courses))
    for course in courses:
        logger = base_logger.bind(
            course={'id': course.id, 'short_name': course.short_name}
        )
        logger.info('Course: {}', course)
        groups = await group_utils.get_groups_by_course(session, course.id)
        if not list(
            filter(
                lambda group: group_schemas.GroupTag.USUAL in group.tags,
                groups,
            )
        ):
            groups.append(
                await _create_group_by_course(
                    session, course, [group_schemas.GroupTag.USUAL], logger
                )
            )
        if course.have_early_exam and not list(
            filter(
                lambda group: group_schemas.GroupTag.EARLY_EXAM in group.tags,
                groups,
            )
        ):
            groups.append(
                await _create_group_by_course(
                    session,
                    course,
                    [group_schemas.GroupTag.EARLY_EXAM],
                    logger,
                )
            )
        await _check_student_for_groups_registration(
            session, course, groups, logger
        )
        await _check_groups_for_contest_registration(
            session, course, groups, logger
        )


async def _create_group_by_course(
    session: AsyncSession,
    course: models.Course,
    tags: list[group_schemas.GroupTag],
    logger: 'loguru.Logger',
) -> models.Group:
    name = (
        course.short_name
        + '-' * (len(tags) > 0)
        + '_'.join(sorted(tags))
    )
    name = name.replace('_', '-')

    group = await group_utils.create_group(session, course, name, tags, logger)
    return group


async def _check_student_for_groups_registration(
    session: AsyncSession,
    course: models.Course,
    groups: list[models.Group],
    base_logger: 'loguru.Logger',
) -> None:
    for group in groups:
        group_logger = base_logger.bind(
            group={
                'id': group.id,
                'yandex_group_id': group.yandex_group_id,
                'name': group.name,
            }
        )
        group_logger.info('Group: {}', group)
        no_registered_students = (
            await student_utils.get_students_by_course_with_no_group(
                session, course, group
            )
        )
        group_logger.info(
            'Group {} has {} no registered students',
            group.name,
            len(no_registered_students),
        )
        count = 0
        for student in no_registered_students:
            student_logger = group_logger.bind(
                student={
                    'id': student.id,
                    'contest_login': student.contest_login,
                }
            )
            try:
                count += await _register_student(
                    session, group, student, student_logger
                )
            except Exception as exc:  # pylint: disable=broad-except
                student_logger.exception(
                    'Error while register student {} in group {}: {}',
                    student.contest_login,
                    group.name,
                    exc,
                )
                await send.send_traceback_message_safe(
                    logger=student_logger,
                    message=f'Error while register '
                    f'student {student.contest_login} '
                    f'in group {group.name}: {exc}',
                    code=traceback.format_exc(),
                )
        group_logger.info(
            'Successfully added {} students to group {}',
            count,
            group.name,
        )


async def _register_student(
    session: AsyncSession,
    group: models.Group,
    student: models.Student,
    logger: 'loguru.Logger',
) -> bool:
    add_ok, message = await group_utils.add_student_to_group(
        session,
        group,
        student,
        logger=logger,
    )
    if not add_ok:
        logger.error(
            'Student {} not registered in group {}. Reason: {}',
            student.contest_login,
            group.name,
            message,
        )
        await send.send_message_safe(
            logger=logger,
            message=f'Student {student.contest_login} not registered in '
            f'group {group.name}. Reason: {message}',
        )
        return False
    await session.commit()
    logger.info(
        'Student {} added to group {}',
        student.contest_login,
        group.name,
    )
    return True


async def _check_groups_for_contest_registration(
    session: AsyncSession,
    course: models.Course,
    groups: list[models.Group],
    base_logger: 'loguru.Logger',
) -> None:
    contests = await contest_utils.get_contests(session, course.id)
    base_logger.info('Course {} has {} contests', course.id, len(contests))
    for contest in contests:
        contest_logger = base_logger.bind(
            contest={
                'id': contest.id,
                'yandex_contest_id': contest.yandex_contest_id,
            }
        )
        contest_logger.info('Contest: {}', contest)
        count = 0
        for group in groups:
            group_logger = contest_logger.bind(
                group={
                    'id': group.id,
                    'yandex_group_id': group.yandex_group_id,
                    'name': group.name,
                }
            )
            need_register = False
            if (
                contest_schemas.ContestTag.EARLY_EXAM in contest.tags
                and group_schemas.GroupTag.EARLY_EXAM in group.tags
            ):
                need_register = True
            if (
                contest_schemas.ContestTag.USUAL in contest.tags
                and group_schemas.GroupTag.USUAL in group.tags
            ):
                need_register = True
            if not need_register:
                group_logger.info(
                    'Group {} no need register in contest {}',
                    group.name,
                    contest.yandex_contest_id,
                )
                continue
            contest_group = await group_utils.get_contest_group_relation(
                session, contest.id, group.id
            )
            if contest_group:
                group_logger.info(
                    'Group {} already registered in contest {}',
                    group.name,
                    contest.yandex_contest_id,
                )
                continue
            group_logger.info(
                'Group {} not registered in contest {}, processing...',
                group.name,
                contest.yandex_contest_id,
            )
            try:
                count += await _register_group(
                    session, contest, group, group_logger
                )
            except Exception as exc:  # pylint: disable=broad-except
                group_logger.exception(
                    'Error while register group {} in contest {}: {}',
                    group.name,
                    contest.yandex_contest_id,
                    exc,
                )
                await send.send_traceback_message_safe(
                    logger=group_logger,
                    message=f'Error while register group {group.name} '
                    f'in contest {contest.yandex_contest_id,}: {exc}',
                    code=traceback.format_exc(),
                )
        contest_logger.info(
            'Successfully added {} groups to contest {}',
            count,
            contest.yandex_contest_id,
        )


async def _register_group(
    session: AsyncSession,
    contest: models.Contest,
    group: models.Group,
    logger: 'loguru.Logger',
) -> bool:
    add_ok, message = await group_utils.add_group_to_contest(
        session,
        contest,
        group,
        logger=logger,
    )
    if not add_ok:
        logger.error(
            'Group {} not registered in contest {}. Reason: {}',
            group.name,
            contest.yandex_contest_id,
            message,
        )
        await send.send_message_safe(
            logger=logger,
            message=f'Group {group.name} not registered in '
            f'contest {contest.yandex_contest_id}. Reason: {message}',
        )
        return False
    await session.commit()
    logger.info(
        'Group {} added to contest {}',
        group.name,
        contest.yandex_contest_id,
    )
    return True

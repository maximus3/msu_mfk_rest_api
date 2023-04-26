# pylint: disable=duplicate-code

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models
from app.schemas import group as group_schemas
from app.utils import yandex_request

from .database import (
    add_contest_group_relation,
    add_student_group_relation,
    create_group_in_db,
)


async def create_group(
    session: AsyncSession,
    course: models.Course,
    name: str,
    tags: list[group_schemas.GroupTag],
    logger: 'loguru.Logger',
) -> models.Group:
    response = await yandex_request.make_request_to_yandex_contest_api(
        'groups/', logger=logger, method='POST', data={'name': name}
    )

    match response.status_code:
        case 400:
            message = f'Group name is invalid: {response.text}'
            raise RuntimeError(message)
        case 401:
            message = f'Yandex API key is invalid. Please check it in .env file: {response.text}'
            raise RuntimeError(message)
        case 403:
            message = f'Yandex API key does not have access to create groups: {response.text}'
            raise RuntimeError(message)
        case 201:
            yandex_group_id = response.json()['id']
            logger.info(
                'Group {} successfully created, yandex_group_id={}',
                name,
                yandex_group_id,
            )
        case _:
            message = (
                f'Unknown error. Status code: {response.status_code}. '
                f'Text: {response.text}'
            )
            raise RuntimeError(message)

    group = await create_group_in_db(
        session=session,
        name=name,
        yandex_group_id=yandex_group_id,
        course_id=course.id,
        tags=tags,
    )
    await session.commit()

    return group


async def add_student_to_group(
    session: AsyncSession,
    group: models.Group,
    student: models.Student,
    logger: 'loguru.Logger',
) -> tuple[bool, str | None]:
    """
    Add student to Yandex Contest group.
    """

    response = await yandex_request.make_request_to_yandex_contest_api(
        f'groups/{group.yandex_group_id}/members',
        logger=logger,
        method='POST',
        data={'login': student.contest_login},
    )

    match response.status_code:
        case 404:
            message = (
                f'Group {group.name} or '
                f'student {student.contest_login} not found'
            )
            return False, message
        case 401:
            message = 'Yandex API key is invalid. Please check it in .env file'
            return False, message
        case 403:
            message = (
                'Yandex API key does not have access to the group '
                f'"{group.name}"'
            )
            return False, message
        case 204:
            logger.info(
                'Student {} successfully added to group {}',
                student.contest_login,
                group.name,
            )
        case _:
            message = (
                f'Unknown error. Status code: {response.status_code}. '
                f'Text: {response.text}'
            )
            return False, message

    await add_student_group_relation(
        session,
        student.id,
        group.id,
    )
    logger.info(
        'Student {} successfully added to group {} in database',
        student.contest_login,
        group.name,
    )
    return True, None


async def add_group_to_contest(
    session: AsyncSession,
    contest: models.Contest,
    group: models.Group,
    logger: 'loguru.Logger',
) -> tuple[bool, str | None]:
    """
    Add group to Yandex contest.
    """

    response = await yandex_request.make_request_to_yandex_contest_api(
        f'contests/{contest.yandex_contest_id}/groups/{group.yandex_group_id}',
        logger=logger,
        method='POST',
        data={'roles': ['PARTICIPANT']},
    )

    match response.status_code:
        case 404:
            message = (
                f'Group {group.name} or '
                f'contest {contest.yandex_contest_id} not found'
            )
            return False, message
        case 401:
            message = 'Yandex API key is invalid. Please check it in .env file'
            return False, message
        case 403:
            message = (
                'Yandex API key does not have access to the group '
                f'"{group.name}"'
            )
            return False, message
        case 204:
            logger.warning(
                'Group {} added to contest {} with code 204',
                group.name,
                contest.yandex_contest_id,
            )
        case 200:
            logger.info(
                'Group {} successfully added to contest {}',
                group.name,
                contest.yandex_contest_id,
            )
        case 400:
            logger.info(
                'Group {} already in contest {}',
                group.name,
                contest.yandex_contest_id,
            )
        case _:
            message = (
                f'Unknown error. Status code: {response.status_code}. '
                f'Text: {response.text}'
            )
            return False, message

    await add_contest_group_relation(
        session,
        contest.id,
        group.id,
    )
    logger.info(
        'Group {} successfully added to contest {} in database',
        group.name,
        contest.yandex_contest_id,
    )
    return True, None

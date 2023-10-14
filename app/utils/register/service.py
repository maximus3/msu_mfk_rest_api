import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import DatabaseStatus, RegisterRequest
from app.schemas import register as register_schemas
from app.utils import student as student_utils
from app.utils.course import (
    add_student_to_course,
    get_course,
    is_student_registered_on_course,
)
from app.utils.department import get_department
from app.utils.student import create_student, get_student


async def register_student_on_course(  # pylint: disable=too-many-return-statements
    session: AsyncSession,
    data: RegisterRequest,
    headers_data: register_schemas.RegisterHeaders,
    logger: 'loguru.Logger',
) -> tuple[DatabaseStatus, str]:
    department = await get_department(session, data.department)
    if department is None:
        logger.info(
            'Register request with department, that not exists: {}',
            data.department,
        )
        return DatabaseStatus.NOT_FOUND, 'Department not found'

    student_by_tg_id = await student_utils.get_student_by_tg_id(
        session, headers_data.tg_id
    )
    if (
        student_by_tg_id
        and student_by_tg_id.yandex_id != headers_data.yandex_id
    ):
        return (
            DatabaseStatus.MANY_TG_ACCOUNTS_ERROR,
            'Кажется, вы пытаетесь зарегистрироваться на курс не через'
            ' тот же яндекс аккаунт, через '
            'который регистрировались до этого.'
            ' Если вы по каким-то причинам хотите поменять аккаунт, '
            'то напишите в поддержку.',
        )

    student_by_login = await get_student(session, headers_data.contest_login)

    if student_by_login and (
        not student_by_tg_id or student_by_login.id != student_by_tg_id.id
    ):
        return (
            DatabaseStatus.MANY_TG_ACCOUNTS_ERROR,
            'Кажется, вы пытаетесь зарегистрироваться на курс не через'
            ' тот же телеграм аккаунт, через '
            'который регистрировались до этого.'
            ' Если вы по каким-то причинам хотите поменять аккаунт, '
            'то напишите в поддержку.',
        )

    if student_by_tg_id:
        if student_by_tg_id.contest_login != headers_data.contest_login:
            logger.info(
                'Student has another prev login: {}, changing to {}',
                student_by_tg_id.contest_login,
                headers_data.contest_login,
            )
            student_by_tg_id.contest_login = headers_data.contest_login
        if student_by_tg_id.token != data.token:
            logger.info(
                'Student has another prev token: {}, changing to {}',
                student_by_tg_id.token,
                data.token,
            )
            student_by_tg_id.token = data.token
    else:
        logger.info('No student with such login and token, creating')
        student_by_tg_id = await create_student(
            session, data, headers_data, department
        )
    await session.commit()

    student = student_by_tg_id

    course = await get_course(session, data.course)
    if course is None:
        return DatabaseStatus.NOT_FOUND, 'Course not found'
    if not course.is_open_registration or course.is_archive:
        return DatabaseStatus.ERROR, 'Registration is closed'
    if await is_student_registered_on_course(session, student.id, course.id):
        return (
            DatabaseStatus.ALREADY_EXISTS,
            'Student already registered on course',
        )
    await add_student_to_course(session, student.id, course.id)
    await session.commit()
    return DatabaseStatus.OK, 'OK'

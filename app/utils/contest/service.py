import logging
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.models import Contest, Student

from .database import add_student_contest_relation


async def add_student_to_contest(
    session: AsyncSession,
    contest: Contest,
    student: Student,
    course_id: UUID,
) -> tuple[bool, str | None]:
    """
    Add student to Yandex contest.
    """
    settings = get_settings()
    logger = logging.getLogger(__name__)

    async with AsyncClient() as client:
        client.headers.update(
            {
                'Authorization': f'OAuth {settings.YANDEX_API_KEY}',
                'Content-Type': 'application/json',
            }
        )
        response = await client.post(
            f'{settings.YANDEX_CONTEST_API_URL}contests/'
            f'{contest.yandex_contest_id}/participants?'
            f'login={student.contest_login}',
        )
        match response.status_code:
            case 404:
                message = f'Contest {contest.yandex_contest_id} not found'
                return False, message
            case 409:
                logger.warning(
                    'Student "%s" already registered on contest "%s"',
                    student.contest_login,
                    contest.yandex_contest_id,
                )
            case 401:
                message = (
                    'Yandex API key is invalid. Please check it in .env file'
                )
                return False, message
            case 403:
                message = (
                    f'Yandex API key does not have access to the contest '
                    f'"{contest.yandex_contest_id}"'
                )
                return False, message
            case 201:
                logger.info(
                    'Student "%s" successfully added to contest "%s"',
                    student.contest_login,
                    contest.yandex_contest_id,
                )
            case 200:
                logger.warning(
                    'Student "%s" already registered on contest "%s" (code 200)',
                    student.contest_login,
                    contest.yandex_contest_id,
                )
            case _:
                message = f'Unknown error. Status code: {response.status_code}'
                return False, message

    await add_student_contest_relation(
        session, student.id, contest.id, course_id
    )
    logger.info(
        'Student "%s" successfully added to contest "%s" in database',
        student.contest_login,
        contest.yandex_contest_id,
    )
    return True, None

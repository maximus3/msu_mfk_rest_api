from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ...database.models import Contest
from .database import add_student_contest_relation


async def add_student_to_contest(
    session: AsyncSession,
    contest: Contest,
    student_id: UUID,
    contest_id: UUID,
    course_id: UUID,
) -> None:
    """
    Add student to Yandex contest.
    """
    print('Add student to contest MOCK')
    print(f'contest: {contest}')
    await add_student_contest_relation(
        session, student_id, contest_id, course_id
    )

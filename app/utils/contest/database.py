from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contest, StudentContest


async def get_all_contests(session: AsyncSession) -> list[Contest]:
    query = select(Contest)
    return (await session.execute(query)).scalars().all()


async def get_contests(
    session: AsyncSession,
    course_id: UUID,
) -> list[Contest]:
    query = select(Contest).where(Contest.course_id == course_id)
    return (await session.execute(query)).scalars().all()


async def is_student_registered_on_contest(
    session: AsyncSession,
    student_id: UUID,
    contest_id: UUID,
) -> bool:
    query = (
        select(StudentContest)
        .where(StudentContest.student_id == student_id)
        .where(StudentContest.contest_id == contest_id)
    )
    return await session.scalar(query) is not None


async def add_student_contest_relation(
    session: AsyncSession,
    student_id: UUID,
    contest_id: UUID,
    course_id: UUID,
) -> None:
    student_contest = StudentContest(
        student_id=student_id,
        contest_id=contest_id,
        course_id=course_id,
    )
    session.add(student_contest)

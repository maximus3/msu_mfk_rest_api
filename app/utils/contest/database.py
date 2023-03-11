from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    Contest,
    ContestLevels,
    StudentContest,
    StudentContestLevels,
)


async def get_all_contests(session: AsyncSession) -> list[Contest]:
    """
    Get all contests in database.

    :param session: Database session

    :return: List of contests
    """
    query = select(Contest)
    return (await session.execute(query)).scalars().all()


async def get_contests(
    session: AsyncSession,
    course_id: UUID,
) -> list[Contest]:
    """
    Get all contests by course id.

    :param session: Database session
    :param course_id: Course id

    :return: List of contests
    """
    query = select(Contest).where(Contest.course_id == course_id)
    return (await session.execute(query)).scalars().fetchall()


async def get_contest_by_id(session: AsyncSession, id_: UUID) -> Contest:
    query = select(Contest).where(Contest.id == id_)
    return await session.scalar(query)


async def get_contest_by_yandex_contest_id(
    session: AsyncSession,
    yandex_contest_id: int,
) -> Contest | None:
    """
    Get contest by yandex contest id.

    :param session: Database session
    :param yandex_contest_id: Yandex contest id

    :return: Contest if exists, None otherwise
    """
    query = select(Contest).where(
        Contest.yandex_contest_id == yandex_contest_id
    )
    return (await session.execute(query)).scalars().first()


async def is_student_registered_on_contest(
    session: AsyncSession,
    student_id: UUID,
    contest_id: UUID,
) -> bool:
    """
    Check if student is registered on contest.

    :param session: Database session
    :param student_id: Student id
    :param contest_id: Contest id

    :return: True if student is registered on contest, False otherwise
    """
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
    author_id: int,
) -> StudentContest:
    """
    Add student contest relation.

    :param session: Database session
    :param student_id: Student id
    :param contest_id: Contest id
    :param course_id: Course id
    :param author_id: Author id in yandex contest

    :return: Student contest relation
    """
    student_contest = StudentContest(
        student_id=student_id,
        contest_id=contest_id,
        course_id=course_id,
        author_id=author_id,
    )
    session.add(student_contest)
    return student_contest


async def get_student_contest_relation(
    session: AsyncSession,
    student_id: UUID,
    contest_id: UUID,
) -> StudentContest | None:
    """
    Get student contest relation if exists.

    :param session: Database session
    :param student_id: Student id
    :param contest_id: Contest id

    :return: Student contest relation if exists, None otherwise
    """
    query = (
        select(StudentContest)
        .where(StudentContest.student_id == student_id)
        .where(StudentContest.contest_id == contest_id)
    )
    return (await session.execute(query)).scalars().first()


async def get_contests_with_relations(
    session: AsyncSession,
    course_id: UUID,
    student_id: UUID,
) -> list[tuple[Contest, StudentContest]]:
    """
    Get contests with relation.

    :param session: Database session
    :param student_id: Student id
    :param course_id: Course id

    :return: List of contests with relation
    """
    query = (
        select(Contest, StudentContest)
        .where(Contest.id == StudentContest.contest_id)
        .where(StudentContest.student_id == student_id)
        .where(StudentContest.course_id == course_id)
    )
    return (await session.execute(query)).fetchall()


async def get_ok_author_ids(
    session: AsyncSession,
    course_id: UUID,
    contest_id: UUID,
) -> list[int]:
    query = (
        select(StudentContest.author_id)
        .where(StudentContest.course_id == course_id)
        .where(StudentContest.contest_id == contest_id)
        .where(StudentContest.is_ok)
    )
    return [author_id for author_id, in await session.execute(query)]


async def get_contest_levels(
    session: AsyncSession, contest_id: UUID
) -> list[ContestLevels]:
    query = select(ContestLevels).where(ContestLevels.contest_id == contest_id)
    return (await session.execute(query)).scalars().all()


async def get_or_create_student_contest_level(
    session: AsyncSession,
    student_id: UUID,
    course_id: UUID,
    contest_id: UUID,
    level_id: UUID,
) -> StudentContestLevels:
    query = (
        select(StudentContestLevels)
        .where(StudentContestLevels.student_id == student_id)
        .where(StudentContestLevels.contest_id == contest_id)
        .where(StudentContestLevels.course_id == course_id)
        .where(StudentContestLevels.contest_level_id == level_id)
    )
    student_contest_level = await session.scalar(query)
    if student_contest_level is None:
        student_contest_level = StudentContestLevels(
            student_id=student_id,
            course_id=course_id,
            contest_id=contest_id,
            contest_level_id=level_id,
        )
        session.add(student_contest_level)
        await session.flush()
    return student_contest_level

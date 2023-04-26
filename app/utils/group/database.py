from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models
from app.schemas import group as group_schemas


async def get_groups_by_course(
    session: AsyncSession, course_id: UUID
) -> list[models.Group]:
    query = select(models.Group).where(models.Group.course_id == course_id)
    return (await session.execute(query)).scalars().all()


async def create_group_in_db(
    session: AsyncSession,
    name: str,
    yandex_group_id: int,
    course_id: UUID,
    tags: list[group_schemas.GroupTag],
) -> models.Group:
    group = models.Group(
        name=name,
        yandex_group_id=yandex_group_id,
        course_id=course_id,
        tags=tags,
    )
    session.add(group)
    return group


async def add_student_group_relation(
    session: AsyncSession,
    student_id: UUID,
    group_id: UUID,
) -> models.StudentGroup:
    """
    Add student group relation.
    """
    student_group = models.StudentGroup(
        group_id=group_id,
        student_id=student_id,
    )
    session.add(student_group)
    return student_group


async def get_contest_group_relation(
    session: AsyncSession,
    contest_id: UUID,
    group_id: UUID,
) -> models.ContestGroup | None:
    """
    Get contest group relation if exists.
    """
    query = (
        select(models.ContestGroup)
        .where(models.ContestGroup.contest_id == contest_id)
        .where(models.ContestGroup.group_id == group_id)
    )
    return (await session.execute(query)).scalars().first()


async def add_contest_group_relation(
    session: AsyncSession,
    contest_id: UUID,
    group_id: UUID,
) -> models.ContestGroup:
    """
    Add contest group relation.
    """
    contest_group = models.ContestGroup(
        contest_id=contest_id,
        group_id=group_id,
    )
    session.add(contest_group)
    return contest_group

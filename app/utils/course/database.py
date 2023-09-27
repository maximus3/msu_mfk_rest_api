from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models
from app.database.models import (
    Course,
    CourseLevels,
    StudentCourse,
    StudentCourseLevels,
)
from app.utils.contest.database import (
    get_contest_levels,
    get_contests_with_relations,
    get_or_create_student_contest_level,
)


async def get_course(session: AsyncSession, name: str) -> Course | None:
    query = select(Course).where(Course.name == name)
    return await session.scalar(query)


async def get_course_by_id(session: AsyncSession, id_: UUID) -> Course:
    query = select(Course).where(Course.id == id_)
    return await session.scalar(query)


async def get_course_by_short_name(
    session: AsyncSession, short_name: str
) -> Course | None:
    query = select(Course).where(Course.short_name == short_name)
    return await session.scalar(query)


async def get_all_active_courses(session: AsyncSession) -> list[Course]:
    query = select(Course).where(~Course.is_archive)
    return (await session.execute(query)).scalars().all()


async def get_all_courses_with_open_registration(
    session: AsyncSession,
) -> list[Course]:
    query = select(Course).where(
        Course.is_open_registration, ~Course.is_archive
    )
    return (await session.execute(query)).scalars().all()


async def get_all_active_courses_with_allowed_smart_suggests(
    session: AsyncSession,
) -> list[Course]:
    query = select(Course).where(
        Course.is_smart_suggests_allowed, ~Course.is_archive
    )
    return (await session.execute(query)).scalars().all()


async def get_student_course(
    session: AsyncSession, student_id: UUID, course_id: UUID
) -> StudentCourse | None:
    query = (
        select(StudentCourse)
        .where(StudentCourse.student_id == student_id)
        .where(StudentCourse.course_id == course_id)
    )
    return await session.scalar(query)


async def is_student_registered_on_course(
    session: AsyncSession, student_id: UUID, course_id: UUID
) -> bool:
    return await get_student_course(session, student_id, course_id) is not None


async def add_student_to_course(
    session: AsyncSession, student_id: UUID, course_id: UUID
) -> None:
    student_course = StudentCourse(
        student_id=student_id,
        course_id=course_id,
    )
    session.add(student_course)


async def get_student_courses(
    session: AsyncSession, student_id: UUID
) -> list[tuple[Course, StudentCourse]]:
    query = (
        select(Course, StudentCourse)
        .where(Course.id == StudentCourse.course_id)
        .where(StudentCourse.student_id == student_id)
        .where(~Course.is_archive)
    )
    return (await session.execute(query)).fetchall()


async def get_course_levels(
    session: AsyncSession, course_id: UUID
) -> list[CourseLevels]:
    query = select(CourseLevels).where(CourseLevels.course_id == course_id)
    return (await session.execute(query)).scalars().all()


async def get_or_create_student_course_level(
    session: AsyncSession, student_id: UUID, course_id: UUID, level_id: UUID
) -> StudentCourseLevels:
    query = (
        select(StudentCourseLevels)
        .where(StudentCourseLevels.student_id == student_id)
        .where(StudentCourseLevels.course_id == course_id)
        .where(StudentCourseLevels.course_level_id == level_id)
    )
    student_course_level = await session.scalar(query)
    if student_course_level is None:
        student_course_level = StudentCourseLevels(
            student_id=student_id,
            course_id=course_id,
            course_level_id=level_id,
        )
        session.add(student_course_level)
        await session.flush()
    return student_course_level


async def get_student_course_contests_data(
    session: AsyncSession,
    course_id: UUID,
    student_id: UUID,
) -> list[
    tuple[
        models.Contest,
        models.StudentContest,
        list[models.ContestLevels],
        list[models.StudentContestLevels],
    ]
]:
    contests_with_relations = sorted(
        await get_contests_with_relations(
            session,
            course_id,
            student_id,
        ),
        key=lambda x: x[0].lecture,
    )
    all_contest_levels = [
        sorted(
            await get_contest_levels(session, contest.id),
            key=lambda x: (x.count_method, x.ok_threshold),
        )
        for contest, _ in contests_with_relations
    ]
    all_student_contest_levels = []
    for (contest, _), contest_levels in zip(
        contests_with_relations, all_contest_levels
    ):
        student_contest_levels = [
            await get_or_create_student_contest_level(
                session, student_id, course_id, contest.id, level.id
            )
            for level in contest_levels
        ]
        all_student_contest_levels.append(student_contest_levels)
    return list(
        map(
            lambda x: (x[0][0], x[0][1], x[1], x[2]),
            zip(
                contests_with_relations,
                all_contest_levels,
                all_student_contest_levels,
            ),
        )
    )

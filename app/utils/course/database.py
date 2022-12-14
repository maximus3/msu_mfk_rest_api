from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Course, StudentCourse


async def get_course(session: AsyncSession, name: str) -> Course | None:
    query = select(Course).where(Course.name == name)
    return await session.scalar(query)


async def get_course_by_short_name(
    session: AsyncSession, short_name: str
) -> Course | None:
    query = select(Course).where(Course.short_name == short_name)
    return await session.scalar(query)


async def get_all_courses(session: AsyncSession) -> list[Course]:
    query = select(Course)
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
    )
    return (await session.execute(query)).fetchall()

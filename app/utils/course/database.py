from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Course, StudentCourse


async def get_course(session: AsyncSession, name: str) -> Course | None:
    query = select(Course).where(Course.name == name)
    return await session.scalar(query)


async def is_student_registered_on_course(
    session: AsyncSession, student_id: UUID, course_id: UUID
) -> bool:
    query = (
        select(StudentCourse)
        .where(StudentCourse.student_id == student_id)
        .where(StudentCourse.course_id == course_id)
    )
    return await session.scalar(query) is not None


async def add_student_to_course(
    session: AsyncSession, student_id: UUID, course_id: UUID
) -> None:
    student_course = StudentCourse(
        student_id=student_id,
        course_id=course_id,
    )
    session.add(student_course)

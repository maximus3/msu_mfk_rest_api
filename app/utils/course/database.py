from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Course, StudentCourse


async def get_course(session: AsyncSession, name: str) -> Course | None:
    query = select(Course).where(Course.name == name)
    return await session.scalar(query)


async def is_student_registered_on_course(
    session: AsyncSession, student_id: int, course_id: int
) -> bool:
    query = (
        select(StudentCourse)
        .where(StudentCourse.mfk_user_id == student_id)
        .where(StudentCourse.course_id == course_id)
    )
    return await session.scalar(query) is not None


async def add_student_to_course(
    session: AsyncSession, student_id: int, course_id: int
) -> None:
    student_course = StudentCourse(
        mfk_user_id=student_id,
        course_id=course_id,
    )
    session.add(student_course)
    await session.refresh(student_course)

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models


async def get_department(
    session: AsyncSession, name: str
) -> models.Department | None:
    query = select(models.Department).where(models.Department.name == name)
    return await session.scalar(query)


async def get_all_departments(
    session: AsyncSession,
) -> list[models.Department]:
    query = select(models.Department)
    return (await session.execute(query)).scalars().all()


async def get_department_by_student(
    session: AsyncSession,
    student_id: uuid.UUID,
) -> models.Department:
    query = (
        select(models.Department)
        .join(models.StudentDepartment)
        .where(models.StudentDepartment.student_id == student_id)
    )
    return await session.scalar(query)

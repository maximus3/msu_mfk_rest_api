from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Student
from app.schemas import DatabaseStatus, RegisterRequest


async def get_student(
    session: AsyncSession, contest_login: str
) -> Student | None:
    query = select(Student).where(Student.contest_login == contest_login)
    return await session.scalar(query)


async def create_student(
    session: AsyncSession, data: RegisterRequest
) -> tuple[DatabaseStatus, str]:
    student = Student(
        fio=data.fio,
        department=data.department,
        contest_login=data.login,
    )
    session.add(student)
    await session.refresh(student)
    return DatabaseStatus.OK, 'OK'

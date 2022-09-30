from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Department, Student, StudentDepartment
from app.schemas import RegisterRequest


async def get_student(
    session: AsyncSession, contest_login: str
) -> Student | None:
    query = select(Student).where(Student.contest_login == contest_login)
    return await session.scalar(query)


async def create_student(
    session: AsyncSession, data: RegisterRequest, department: Department
) -> Student:
    student = Student(
        fio=data.fio,
        contest_login=data.login,
        token=data.token,
    )
    session.add(student)
    session.add(
        StudentDepartment(student_id=student.id, department_id=department.id)
    )
    await session.refresh(student)
    return student

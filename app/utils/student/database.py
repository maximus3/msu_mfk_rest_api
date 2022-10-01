from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    Department,
    Student,
    StudentCourse,
    StudentDepartment,
)
from app.schemas import RegisterRequest


async def get_student(
    session: AsyncSession, contest_login: str
) -> Student | None:
    query = select(Student).where(Student.contest_login == contest_login)
    return await session.scalar(query)


async def get_students_by_course(
    session: AsyncSession, course_id: UUID
) -> list[Student]:
    query = (
        select(Student)
        .join(StudentCourse)
        .where(StudentCourse.course_id == course_id)
    )
    return (await session.execute(query)).scalars().all()


async def create_student(
    session: AsyncSession, data: RegisterRequest, department: Department
) -> Student:
    student = Student(
        fio=data.fio,
        contest_login=data.contest_login,
        token=data.token,
    )
    session.add(student)
    await session.flush()
    await session.refresh(student)
    session.add(
        StudentDepartment(student_id=student.id, department_id=department.id)
    )
    return student

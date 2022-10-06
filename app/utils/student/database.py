from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    Department,
    Student,
    StudentContest,
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
    return (await session.execute(query)).scalars().fetchall()


async def get_students_by_course_with_no_contest(
    session: AsyncSession, course_id: UUID, contest_id: UUID
) -> list[Student]:
    query = (
        select(Student, StudentCourse, StudentContest)
        .join(StudentCourse, StudentCourse.student_id == Student.id)
        .where(StudentCourse.course_id == course_id)
        .join(
            StudentContest,
            and_(
                StudentContest.student_id == Student.id,
                StudentContest.contest_id == contest_id,
            ),
            isouter=True,
        )
        .where(StudentContest.id.is_(None))
    )
    data = (await session.execute(query)).fetchall()
    return [x[0] for x in data]


async def get_students_by_course_with_department(
    session: AsyncSession, course_id: UUID
) -> list[tuple[Student, Department]]:
    query = (
        select(Student, Department)
        .join(StudentCourse)
        .join(StudentDepartment)
        .join(Department)
        .where(StudentCourse.course_id == course_id)
    )
    return (await session.execute(query)).fetchall()


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

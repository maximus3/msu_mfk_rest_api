from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models
from app.database.models import (
    Department,
    Student,
    StudentContest,
    StudentCourse,
    StudentDepartment,
)
from app.schemas import RegisterRequest
from app.schemas import group as group_schemas
from app.schemas import register as register_schemas


async def get_student(
    session: AsyncSession, contest_login: str
) -> Student | None:
    query = select(Student).where(Student.contest_login == contest_login)
    return await session.scalar(query)


async def get_student_by_token(
    session: AsyncSession, token: str
) -> Student | None:
    query = select(Student).where(Student.token == token)
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


async def get_students_by_course_with_no_group(
    session: AsyncSession, course: models.Course, group: models.Group
) -> list[Student]:
    if group_schemas.GroupTag.EARLY_EXAM in group.tags:
        student_course_request = and_(
            models.StudentCourse.student_id == models.Student.id,
            models.StudentCourse.allow_early_exam,
        )
    else:
        student_course_request = (
            models.StudentCourse.student_id == models.Student.id
        )
    query = (
        select(models.Student, models.StudentCourse, models.StudentGroup)
        .join(models.StudentCourse, student_course_request)
        .where(models.StudentCourse.course_id == course.id)
        .join(
            models.StudentGroup,
            and_(
                models.StudentGroup.student_id == Student.id,
                models.StudentGroup.group_id == group.id,
            ),
            isouter=True,
        )
        .where(models.StudentGroup.id.is_(None))
    )
    data = (await session.execute(query)).fetchall()
    return [x[0] for x in data]


async def get_students_by_course_with_department(
    session: AsyncSession, course_id: UUID
) -> list[tuple[Student, StudentCourse, Department]]:
    query = (
        select(Student, StudentCourse, Department)
        .join(StudentCourse)
        .where(StudentCourse.course_id == course_id)
        .join(StudentDepartment, isouter=True)
        .join(Department, isouter=True)
    )
    return (await session.execute(query)).fetchall()


async def create_student(
    session: AsyncSession,
    data: RegisterRequest,
    headers_data: register_schemas.RegisterHeaders,
    department: Department,
) -> Student:
    student = Student(
        fio=data.fio,
        contest_login=headers_data.contest_login,
        tg_id=headers_data.tg_id,
        tg_username=headers_data.tg_username,
        bm_id=headers_data.bm_id,
        token=data.token,
    )
    session.add(student)
    await session.flush()
    await session.refresh(student)
    session.add(
        StudentDepartment(student_id=student.id, department_id=department.id)
    )
    return student


async def get_student_by_fio(
    session: AsyncSession, fio: str
) -> Student | None:
    query = select(Student).where(func.lower(Student.fio) == fio.lower())
    return await session.scalar(query)


async def get_or_create_all_student_models(
    session: AsyncSession,
    course_id: UUID,
    contest_id: UUID,
    author_id: int,
) -> tuple[Student | None, StudentCourse | None, StudentContest | None]:
    student_contest: StudentContest = await session.scalar(
        select(StudentContest)
        .where(StudentContest.contest_id == contest_id)
        .where(StudentContest.course_id == course_id)
        .where(StudentContest.author_id == author_id)
    )
    if student_contest is None:
        return None, None, None
    student: Student = await session.scalar(
        select(Student).where(Student.id == student_contest.student_id)
    )
    student_course: StudentCourse = await session.scalar(
        select(StudentCourse)
        .where(StudentCourse.course_id == course_id)
        .where(StudentCourse.student_id == student.id)
    )

    return student, student_course, student_contest

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models


async def get_task(
    session: AsyncSession, contest_id: UUID, yandex_task_id: str
) -> models.Task | None:
    query = (
        select(models.Task)
        .where(models.Task.yandex_task_id == yandex_task_id)
        .where(models.Task.contest_id == contest_id)
    )
    return await session.scalar(query)


async def get_student_task_relation(
    session: AsyncSession,
    student_id: UUID,
    task_id: UUID,
) -> models.StudentTask | None:
    """
    Get student task relation if exists.

    :param session: Database session
    :param student_id: Student id
    :param task_id: Task id

    :return: Student task relation if exists, None otherwise
    """
    query = (
        select(models.StudentTask)
        .where(models.StudentTask.student_id == student_id)
        .where(models.StudentTask.task_id == task_id)
    )
    return (await session.execute(query)).scalars().first()


async def add_student_task_relation(
    session: AsyncSession,
    student: models.Student,
    contest: models.Contest,
    course: models.Course,
    task: models.Task,
) -> models.StudentTask:
    """
    Add student task relation.

    :param session: Database session
    :param student: Student models
    :param contest: Contest models
    :param course: Course models
    :param task: Task model

    :return: Student task relation
    """
    student_task = models.StudentTask(
        course_id=course.id,
        contest_id=contest.id,
        task_id=task.id,
        student_id=student.id,
    )
    session.add(student_task)
    return student_task

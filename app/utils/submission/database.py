from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import models
from app.schemas import contest as contest_schemas


async def get_last_updated_submission(
    session: AsyncSession, contest_id: UUID
) -> int | None:
    query = (
        select(models.Submission)
        .where(models.Submission.contest_id == contest_id)
        .order_by(models.Submission.run_id.desc())
        .limit(1)
    )
    return await session.scalar(query)


async def get_submission(
    session: AsyncSession,
    run_id: int,
) -> models.Submission | None:
    query = select(models.Submission).where(models.Submission.run_id == run_id)
    return (await session.execute(query)).scalars().first()


async def add_submission(  # pylint: disable=too-many-arguments
    session: AsyncSession,
    student: models.Student,
    contest: models.Contest,
    course: models.Course,
    task: models.Task,
    student_task: models.StudentTask,
    submission: contest_schemas.ContestSubmissionFull,
) -> models.Submission:
    no_deadline_score = (
        task.score_max
        if (
            not submission.finalScore
            and submission.verdict == 'OK'
            and task.is_zero_ok
        )
        else submission.finalScore
    )
    final_score = (
        no_deadline_score
        if submission.submissionTime <= contest.deadline
        else 0
    )
    submission_model = models.Submission(
        course_id=course.id,
        contest_id=contest.id,
        task_id=task.id,
        student_id=student.id,
        student_task_id=student_task.id,
        author_id=submission.authorId,
        run_id=submission.id,
        verdict=submission.verdict,
        final_score=final_score,
        no_deadline_score=no_deadline_score,
        submission_link=f'https://admin.contest.yandex.ru/'
        f'submissions/{submission.id}/',
        time_from_start=submission.timeFromStart,
        submission_time=submission.submissionTime,
    )
    session.add(submission_model)
    return submission_model

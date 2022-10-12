from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import ContestResults, CourseResults, StudentResults
from app.utils.contest import get_contests_with_relations
from app.utils.course import get_student_courses
from app.utils.student import get_student
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/results',
    tags=['Results'],
)


@api_router.get(
    '/all/{student_login}',
    response_model=StudentResults,
    status_code=status.HTTP_200_OK,
)
async def get_all_results(
    student_login: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> StudentResults:
    """
    Get student results for a specific course.
    """
    student = await get_student(session, student_login)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Student not found',
        )
    return StudentResults(
        courses=[
            CourseResults(
                name=course.name,
                contests=[
                    ContestResults(
                        link=contest.link,
                        tasks_count=contest.tasks_count,
                        tasks_need=contest.tasks_need,
                        tasks_done=student_contest.tasks_done,
                        is_ok=student_contest.is_ok,
                        updated_at=datetime.strftime(
                            student_contest.updated_at,
                            '%Y-%m-%d %H:%M:%S',
                        ),
                    )
                    for contest, student_contest in await get_contests_with_relations(  # pylint: disable=line-too-long
                        session,
                        course.id,
                        student.id,
                    )
                ],
            )
            for course in await get_student_courses(session, student.id)
        ]
    )

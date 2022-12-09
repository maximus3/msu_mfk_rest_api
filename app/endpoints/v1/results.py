from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import ContestResults, CourseResults, StudentResults
from app.utils.common import fill_pdf, get_datetime_msk_tz
from app.utils.contest import get_contests_with_relations
from app.utils.course import get_course_by_short_name, get_student_courses
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
                        score_max=contest.score_max,
                        levels_count=contest.levels['count']
                        if contest.levels
                        else 0,
                        levels=sorted(
                            contest.levels['levels'],
                            key=lambda level: level['score_need'],
                        )
                        if contest.levels
                        else [],
                        lecture=contest.lecture,
                        tasks_done=student_contest.tasks_done or 0,
                        score=student_contest.score or 0,
                        is_ok=student_contest.is_ok,
                        updated_at=get_datetime_msk_tz(
                            student_contest.dt_updated
                        ).strftime(
                            '%Y-%m-%d %H:%M:%S',
                        ),
                        deadline=get_datetime_msk_tz(
                            contest.deadline,
                        ).strftime(
                            '%Y-%m-%d %H:%M:%S',
                        ),
                    )
                    for contest, student_contest in sorted(
                        await get_contests_with_relations(
                            session,
                            course.id,
                            student.id,
                        ),
                        key=lambda x: x[0].lecture,
                    )
                ],
            )
            for course in await get_student_courses(session, student.id)
        ]
    )


@api_router.post(
    '/fill/{course_short_name}',
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def fill_results(
    file: UploadFile,
    course_short_name: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> dict[str, str]:
    course = await get_course_by_short_name(session, course_short_name)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Course not found',
        )
    with open('temp.pdf', 'wb') as f:
        f.write(await file.read())
    result_filename = await fill_pdf('temp.pdf', course.id, session)
    Path('temp.pdf').unlink()
    return {'filename': result_filename}

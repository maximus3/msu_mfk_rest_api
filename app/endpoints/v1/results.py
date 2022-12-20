from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import StudentResults
from app.utils.common import fill_pdf
from app.utils.course import get_course_by_short_name, get_student_courses
from app.utils.results import get_student_course_results
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
            await get_student_course_results(
                student, course, student_course, session
            )
            for course, student_course in await get_student_courses(
                session, student.id
            )
        ],
        fio=student.fio,
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
) -> FileResponse:
    course = await get_course_by_short_name(session, course_short_name)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Course not found',
        )
    with open('temp.pdf', 'wb') as f:
        f.write(await file.read())
    result_path = await fill_pdf(
        'temp.pdf',
        course.id,
        session,
        result_filename=f'{course_short_name}_{file.filename}.pdf',
    )
    Path('temp.pdf').unlink()
    return FileResponse(
        result_path,
        media_type='application/octet-stream',
        filename=result_path.name,
    )

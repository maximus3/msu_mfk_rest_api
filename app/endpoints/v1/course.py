from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import responses

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import CourseResponse
from app.schemas import course as course_schemas
from app.utils import course as course_utils
from app.utils import student as student_utils
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/course',
    tags=['Courses'],
)


@api_router.get(
    '',
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    description='Courses with open registration',
)
async def get(
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> CourseResponse:
    courses = await course_utils.get_all_courses_with_open_registration(
        session
    )
    return CourseResponse(items=courses)


@api_router.post(
    '',
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    description='Get course by name',
)
async def post(
    course_name_request: course_schemas.CourseNameRequest,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> CourseResponse:
    course = await course_utils.get_course(session, course_name_request.name)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Course not found',
        )
    return CourseResponse(items=[course])


@api_router.get(
    '/by-student/{student_login}',
    status_code=status.HTTP_200_OK,
    response_model=CourseResponse,
    description='Courses with open registration by student',
)
async def get_by_student(
    student_login: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> responses.JSONResponse:
    headers = {'log_contest_login': student_login}
    student = await student_utils.get_student_or_raise(
        session, student_login, headers=headers
    )
    courses = list(
        map(
            lambda elem: elem[0],
            await course_utils.get_student_courses(session, student.id),
        )
    )
    return responses.JSONResponse(
        CourseResponse(items=courses),
        headers=headers,
    )

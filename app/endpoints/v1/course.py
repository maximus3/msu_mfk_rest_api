from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import CourseResponse
from app.utils.course import get_all_courses
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/course',
    tags=['Courses'],
)


@api_router.get(
    '',
    status_code=status.HTTP_200_OK,
)
async def get(
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> CourseResponse:
    courses = await get_all_courses(session)
    return CourseResponse(items=courses)

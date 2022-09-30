from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import DatabaseStatus, RegisterRequest, RegisterResponse
from app.utils.register import register_student_on_course
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/register',
    tags=['Register new student on course'],
)


@api_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> RegisterResponse:
    result_status, message = await register_student_on_course(session, data)
    if result_status == DatabaseStatus.OK:
        return RegisterResponse(contest_login=data.contest_login)
    if result_status == DatabaseStatus.ALREADY_EXISTS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )
    if result_status == DatabaseStatus.NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
    raise HTTPException(status_code=500, detail=message)

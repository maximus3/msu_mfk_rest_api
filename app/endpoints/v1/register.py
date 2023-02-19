import loguru
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

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
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: Request,
    data: RegisterRequest,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> RegisterResponse:
    logger = loguru.logger.bind(uuid=request['request_id'])
    result_status, message = await register_student_on_course(
        session, data, logger=logger
    )
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
    if (
        result_status == DatabaseStatus.ERROR
        and message == 'Registration is closed'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    raise HTTPException(status_code=500, detail=message)

import loguru
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

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
) -> JSONResponse:
    logger = loguru.logger.bind(
        uuid=request['request_id'],
        student={
            'contest_login': data.contest_login,
            'course': data.course,
            'department': data.department,
        },
    )
    headers = {'log_contest_login': data.contest_login}
    result_status, message = await register_student_on_course(
        session, data, logger=logger
    )
    if result_status == DatabaseStatus.OK:
        return JSONResponse(
            RegisterResponse(contest_login=data.contest_login).dict(),
            headers=headers,
        )
    if result_status == DatabaseStatus.ALREADY_EXISTS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
            headers=headers,
        )
    if result_status == DatabaseStatus.NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
            headers=headers,
        )
    if (
        result_status == DatabaseStatus.ERROR
        and message == 'Registration is closed'
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            headers=headers,
        )
    raise HTTPException(status_code=500, detail=message, headers=headers)

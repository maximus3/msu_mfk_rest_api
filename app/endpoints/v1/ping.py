from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import PingMessage, PingResponse
from app.utils.health_check import health_check_db
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/health_check',
    tags=['Application Health'],
)


@api_router.get(
    '/ping_application',
    response_model=PingResponse,
    status_code=status.HTTP_200_OK,
)
async def ping_application(
    _: Request,
) -> PingResponse:
    return PingResponse(message=PingMessage.OK)


@api_router.get(
    '/ping_database',
    response_model=PingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'description': PingMessage.DB_ERROR
        }
    },
)
async def ping_database(
    _: Request,
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> PingResponse:
    if await health_check_db(session):
        return PingResponse(message=PingMessage.OK)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=PingMessage.DB_ERROR,
    )


@api_router.get(
    '/ping_auth',
    response_model=PingResponse,
    status_code=status.HTTP_200_OK,
)
async def ping_auth(
    _: Request,
    user: User = Depends(get_current_user),
) -> PingResponse:
    return PingResponse(message=PingMessage.OK, detail=user.username)

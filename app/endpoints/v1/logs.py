from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse

from app.database.models import User
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/logs',
    tags=['Application Logs'],
)


@api_router.get(
    '',
    status_code=status.HTTP_200_OK,
)
async def get(
    _: Request,
    __: User = Depends(get_current_user),
    last: int = 100,
) -> PlainTextResponse:
    with open('logfile.log', 'r', encoding='windows-1251') as f:
        lines = f.readlines()
    return PlainTextResponse(''.join(lines[-last:]))


@api_router.post(
    '/to_text',
    status_code=status.HTTP_200_OK,
)
async def to_text(
    _: Request,
    __: User = Depends(get_current_user),
    data: dict[Any, Any] | None = None,
) -> PlainTextResponse:
    data = data or {}
    return PlainTextResponse(str(data))

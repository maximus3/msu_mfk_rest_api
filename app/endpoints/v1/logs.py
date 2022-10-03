from pathlib import Path

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import PlainTextResponse

from app.config import get_settings
from app.database.models import User
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/logs',
    tags=['Application Logs'],
)


@api_router.get(
    '/app',
    status_code=status.HTTP_200_OK,
)
async def get(
    _: Request,
    __: User = Depends(get_current_user),
    last: int = 100,
) -> PlainTextResponse:
    settings = get_settings()
    if not Path(settings.LOGGING_APP_FILE).exists():
        return PlainTextResponse('No logs yet')
    lines = []
    for encoding in ['utf-8', 'cp1252', 'iso-8859-1']:
        try:
            with open(settings.LOGGING_APP_FILE, 'r', encoding=encoding) as f:
                lines = f.readlines()
                break
        except UnicodeDecodeError:
            continue
    return PlainTextResponse(''.join(lines[-last:]))

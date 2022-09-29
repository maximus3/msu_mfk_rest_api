from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import FileResponse

from app.database.models import User
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/logs',
    tags=['Application Logs'],
)


@api_router.get(
    '/get',
    status_code=status.HTTP_200_OK,
)
async def get(
    _: Request,
    __: User = Depends(get_current_user),
) -> FileResponse:
    return FileResponse(
        path='logfile.log',
        media_type='application/ctet-stream',
        filename='logfile.log',
    )

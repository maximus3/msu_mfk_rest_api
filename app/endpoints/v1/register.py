from fastapi import APIRouter, Depends, status

from app.database.models import User
from app.schemas import RegisterRequest
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/register',
    tags=['Register new msu mfk user'],
)


@api_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    _: User = Depends(get_current_user),
) -> RegisterRequest:
    return data

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.database.models import User
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/register',
    tags=['Register new msu mfk user'],
)


class RegisterRequest(BaseModel):
    fio: str
    department: str
    login: str


@api_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    _: User = Depends(get_current_user),
) -> RegisterRequest:
    return data

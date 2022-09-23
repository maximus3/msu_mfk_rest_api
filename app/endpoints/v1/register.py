from fastapi import APIRouter, status
from pydantic import BaseModel


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
) -> RegisterRequest:
    return data

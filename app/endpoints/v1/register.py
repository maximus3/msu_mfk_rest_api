from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import PingMessage, PingResponse
from app.utils.health_check import health_check_db
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
    status_code=status.HTTP_201_OK,
)
async def register(
    data: RegisterRequest,
):
    return data

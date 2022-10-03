from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import DepartmentResponse
from app.utils.department import get_all_departments
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/department',
    tags=['Departments'],
)


@api_router.get(
    '',
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get(
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> DepartmentResponse:
    departments = await get_all_departments(session)
    return DepartmentResponse(items=departments)

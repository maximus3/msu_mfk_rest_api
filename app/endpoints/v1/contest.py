from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import Contest, User
from app.schemas import ContestCreateRequest, ContestInfoResponse
from app.utils.contest import (
    get_contest_by_yandex_contest_id,
    get_contest_info,
)
from app.utils.course import get_course_by_short_name
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/contest',
    tags=['Contests'],
)


@api_router.post(
    '',
    response_model=ContestInfoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    contest_request: ContestCreateRequest,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> ContestInfoResponse:
    course = await get_course_by_short_name(
        session, contest_request.course_short_name
    )
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Course not found',
        )
    contest = await get_contest_by_yandex_contest_id(
        session, contest_request.yandex_contest_id
    )
    if contest is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Contest already exists',
        )
    contest_info = await get_contest_info(contest_request.yandex_contest_id)
    contest = Contest(
        yandex_contest_id=contest_request.yandex_contest_id,
        lecture=contest_request.lecture,
        is_necessary=contest_request.is_necessary,
        course_id=course.id,
        link='https://contest.yandex.ru/contest/'
        + str(contest_request.yandex_contest_id),
        score_max=contest_request.score_max,
        levels=contest_request.levels.dict()
        if contest_request.levels
        else None,
        deadline=contest_info.deadline,
        tasks_count=contest_info.tasks_count,
    )
    session.add(contest)
    await session.commit()
    return ContestInfoResponse(
        course_short_name=course.short_name,
        yandex_contest_id=contest.yandex_contest_id,
        deadline=contest.deadline,
        lecture=contest.lecture,
        link=contest.link,
        tasks_count=contest.tasks_count,
        score_max=contest.score_max,
        levels=contest.levels,
        is_necessary=contest.is_necessary,
    )

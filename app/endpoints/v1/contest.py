import loguru
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.database import models
from app.database.connection import SessionManager
from app.database.models import Contest, User
from app.schemas import ContestCreateRequest, ContestInfoResponse
from app.schemas.contest import ContestTag
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
    request: Request,
    contest_request: ContestCreateRequest,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> ContestInfoResponse:
    logger = loguru.logger.bind(uuid=request['request_id'])
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
    contest_info = await get_contest_info(
        contest_request.yandex_contest_id, logger=logger
    )
    tags = []
    if contest_request.is_necessary:
        tags.append(ContestTag.NECESSARY)
    if contest_request.is_final:
        tags.append(ContestTag.FINAL)
    contest = Contest(
        yandex_contest_id=contest_request.yandex_contest_id,
        lecture=contest_request.lecture,
        tags=tags,
        course_id=course.id,
        link='https://contest.yandex.ru/contest/'
        + str(contest_request.yandex_contest_id),
        score_max=contest_request.score_max,
        deadline=contest_info.deadline,
        tasks_count=contest_info.tasks_count,
        default_final_score_evaluation_formula=contest_request.default_final_score_evaluation_formula  # pylint: disable=line-too-long
        or course.default_final_score_evaluation_formula,
        name_format=contest_request.name_format,
    )
    course.score_max += contest_request.score_max
    course.contest_count += 1
    session.add(contest)
    session.add(course)
    await session.flush()
    for task in contest_info.tasks:
        session.add(
            models.Task(
                contest_id=contest.id,
                yandex_task_id=task.yandex_task_id,
                name=task.name,
                alias=task.alias,
                is_zero_ok=False,  # TODO: need change in db next
                score_max=0,  # TODO: need change in db next
                final_score_evaluation_formula=contest.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
            )
        )
    await session.flush()
    if contest_request.levels:
        for level in contest_request.levels.items:
            session.add(
                models.ContestLevels(
                    course_id=course.id,
                    contest_id=contest.id,
                    level_name=level.name,
                    level_ok_method=level.ok_method,
                    count_method=level.count_method,
                    ok_threshold=level.ok_threshold,
                    include_after_deadline=level.include_after_deadline,
                )
            )
    await session.commit()
    return ContestInfoResponse(
        course_short_name=course.short_name,
        yandex_contest_id=contest.yandex_contest_id,
        deadline=contest.deadline,
        lecture=contest.lecture,
        link=contest.link,
        tasks_count=contest.tasks_count,
        score_max=contest.score_max,
        is_necessary=ContestTag.NECESSARY in contest.tags,
    )

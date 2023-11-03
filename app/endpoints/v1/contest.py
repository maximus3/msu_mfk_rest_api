import loguru
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.database import models
from app.database.connection import SessionManager
from app.database.models import Contest, User
from app.schemas import ContestCreateRequest, ContestInfoResponse
from app.schemas.contest import ContestTag, TaskInfoResponse
from app.utils import task as task_utils
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
async def create(  # pylint: disable=too-many-statements
    _: Request,
    contest_request: ContestCreateRequest,
    __: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> ContestInfoResponse:
    logger = loguru.logger.bind(
        course={'short_name': contest_request.course_short_name},
        department={'yandex_contest_id': contest_request.yandex_contest_id},
    )
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
        contest_request.yandex_contest_id, logger=loguru.logger
    )
    tags = []
    if contest_request.is_necessary:
        tags.append(ContestTag.NECESSARY)
    if contest_request.is_final:
        tags.append(ContestTag.FINAL)
    if contest_request.is_usual:
        tags.append(ContestTag.USUAL)
    if contest_request.is_early_exam:
        tags.append(ContestTag.EARLY_EXAM)
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

    all_tasks_exists = await task_utils.get_tasks_by_yandex_ids(
        session=session,
        yandex_task_ids=[task.yandex_task_id for task in contest_info.tasks],
    )

    created_tasks = []

    for task in contest_info.tasks:
        is_zero_ok = False  # TODO: need change in db next
        score_max = 0  # TODO: need change in db next

        tasks_exists = [
            task_exist
            for task_exist in all_tasks_exists
            if task_exist.yandex_task_id == task.yandex_task_id
        ]

        is_zero_ok_set = set(
            task_exist.is_zero_ok for task_exist in tasks_exists
        )
        score_max_set = set(
            task_exist.score_max for task_exist in tasks_exists
        )
        logger.info(
            'Got {} task_exists for yandex_task_id={} '
            'is_zero_ok_set={} score_max_set={}',
            len(tasks_exists),
            task.yandex_task_id,
            is_zero_ok_set,
            score_max_set,
        )
        if len(is_zero_ok_set) == 1:
            is_zero_ok = is_zero_ok_set.pop()
            logger.info(
                'Got is_zero_ok={} for task {} ({}) from old tasks',
                is_zero_ok,
                task.alias,
                task.yandex_task_id,
            )
        if len(score_max_set) == 1:
            score_max = score_max_set.pop()
            logger.info(
                'Got score_max={} for task {} ({}) from old tasks',
                score_max,
                task.alias,
                task.yandex_task_id,
            )

        task_model = models.Task(
            contest_id=contest.id,
            yandex_task_id=task.yandex_task_id,
            name=task.name,
            alias=task.alias,
            is_zero_ok=is_zero_ok,
            score_max=score_max,
            final_score_evaluation_formula=contest.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
        )
        session.add(task_model)
        created_tasks.append(task_model)
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
        tasks=[
            TaskInfoResponse(
                alias=created_task.alias,
                yandex_task_id=created_task.yandex_task_id,
                name=created_task.name,
                is_zero_ok=created_task.is_zero_ok,
                score_max=created_task.score_max,
            )
            for created_task in sorted(created_tasks, key=lambda x: x.alias)
        ],
    )

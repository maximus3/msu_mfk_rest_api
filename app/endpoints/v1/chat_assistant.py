import loguru
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import requests
from starlette.responses import JSONResponse

from app import worker
from app.database import models
from app.database.connection import SessionManager
from app.limiter import limiter
from app.schemas import chat_assistant as chat_assistant_schemas
from app.utils import contest as contest_utils
from app.utils import course as course_utils
from app.utils import task as task_utils
from app.utils import user as user_utils


api_router = APIRouter(
    prefix='/chat_assistant',
    tags=['Chat Assistant'],
)


@api_router.post(
    '',
    status_code=status.HTTP_200_OK,
)
@limiter.limit(
    '10/1day', key_func=lambda request: request.headers['log-tg-id']
)
@limiter.limit(
    '1/2minute', key_func=lambda request: request.headers['log-tg-id']
)
async def chat_assistant(
    request: requests.Request,
    chat_assistant_request: chat_assistant_schemas.ChatAssistantRequest,
    _: models.User = Depends(user_utils.get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> JSONResponse:
    course = await course_utils.get_course(
        session=session, name=chat_assistant_request.course_name
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Курс не найден.'
        )
    if not course.is_smart_suggests_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Для курса {course.name} нет умных подсказок.',
        )
    contest = await contest_utils.get_contest_by_lecture(
        session=session,
        course_id=course.id,
        lecture=chat_assistant_request.contest_number,
    )
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Контест {chat_assistant_request.contest_number} '
            f'не найден для курса {course.name}',
        )
    task_number = chat_assistant_request.task_number.split('.')[0]
    task = await task_utils.get_task_by_alias(
        session=session,
        contest_id=contest.id,
        alias=task_number,
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'В контесте {chat_assistant_request.contest_number} '
            f'для курса {course.name} не найдена задача '
            f'номер {task_number}',
        )
    logger = loguru.logger.bind(
        course={'name': course.name, 'short_name': course.short_name},
        contest={'yandex_contest_id': contest.yandex_contest_id},
        task={'yandex_task_id': task.yandex_task_id},
    )

    celery_task = worker.get_assistant_answer_task.delay(
        data_raw=chat_assistant_schemas.ChatAssistantServerRequest(
            contest_number=contest.lecture,
            task_number=task.alias,
            user_query=chat_assistant_request.user_query,
        ).dict(),
        request_id=request.scope['request_id'],
    )
    logger = logger.bind(
        task_id=celery_task.id,
    )
    logger.info('Task {} sent to celery', celery_task.id)
    return JSONResponse({'task_id': celery_task.id})

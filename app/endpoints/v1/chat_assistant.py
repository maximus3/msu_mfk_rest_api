import loguru
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import requests

from app.database import models
from app.database.connection import SessionManager
from app.schemas import chat_assistant as chat_assistant_schemas
from app.utils import chat_assistant as chat_assistant_utils
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
    response_model=chat_assistant_schemas.ChatAssistantResponse,
    status_code=status.HTTP_200_OK,
)
async def chat_assistant(
    _: requests.Request,
    chat_assistant_request: chat_assistant_schemas.ChatAssistantRequest,
    __: models.User = Depends(user_utils.get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> chat_assistant_schemas.ChatAssistantResponse:
    logger = loguru.logger.bind(
        course={'name': chat_assistant_request.course_name},
    )
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
    task = await task_utils.get_task_by_alias(
        session=session,
        contest_id=contest.id,
        alias=str(chat_assistant_request.task_number),
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'В контесте {chat_assistant_request.contest_number} '
            f'для курса {course.name} не найдена задача '
            f'номер {chat_assistant_request.task_number}',
        )
    logger = loguru.logger.bind(
        course={'name': course.name, 'short_name': course.short_name},
        contest={'yandex_contest_id': contest.yandex_contest_id},
        task={'yandex_task_id': task.yandex_task_id},
    )
    result = await chat_assistant_utils.get_chat_assistant_suggest(
        logger=logger,
        data=chat_assistant_schemas.ChatAssistantServerRequest(
            contest_number=chat_assistant_request.contest_number,
            task_number=chat_assistant_request.task_number,
            user_query=chat_assistant_request.user_query,
        ),
    )
    if not result.result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Error in getting answer, try again later.',
        )
    return chat_assistant_schemas.ChatAssistantResponse(
        answer=result.result,
    )

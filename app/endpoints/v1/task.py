import fastapi
import loguru
from celery import result as celery_result
from starlette import requests, responses, status

from app.database import models
from app.utils import user as user_utils


api_router = fastapi.APIRouter(
    prefix='/task',
    tags=['Task'],
)


@api_router.get(
    '/result',
    status_code=status.HTTP_200_OK,
)
async def get_task_result(
    request: requests.Request,  # pylint: disable=unused-argument
    task_id: str,
    _: models.User = fastapi.Depends(user_utils.get_current_user),
) -> responses.JSONResponse:
    SUCCESS_STATUS = 'SUCCESS'
    logger = loguru.logger.bind(
        task_id=task_id,
    )
    result = celery_result.AsyncResult(task_id)
    logger.info('Current task status: {}', result.status)
    messages = None
    if result.ready():
        if result.status != SUCCESS_STATUS:
            messages = [
                'Произошла ошибка. Попробуйте еще раз '
                'или напишите администратору.'
            ]
        else:
            messages = result.result

    return responses.JSONResponse(
        {
            'ready': result.ready(),
            'messages': messages,
        }
    )

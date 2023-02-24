import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from app.config import get_settings
from app.database.models import User
from app.schemas import logs as logs_schemas
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/logs',
    tags=['Application Logs'],
)


@api_router.get(
    '/app',
    status_code=status.HTTP_200_OK,
)
async def get(  # pylint: disable=too-many-statements
    _: Request,
    __: User = Depends(get_current_user),
    last: int = 100,
    log_id: str | None = None,
    student_login: str | None = None,
    log_name: str | None = None,
    log_file: str = 'app',
) -> logs_schemas.LogsResponse:
    settings = get_settings()
    response = logs_schemas.LogsResponse(items=[], count=0)
    if log_file == 'app':
        log_filename = settings.LOGGING_APP_FILE
    elif log_file == 'scheduler':
        log_filename = settings.LOGGING_SCHEDULER_FILE
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Log file not found',
        )
    if not Path(log_filename).exists():
        return response
    for encoding in ['utf-8', 'cp1252', 'iso-8859-1']:
        try:
            with open(log_filename, 'r', encoding=encoding) as f:
                for line in f:
                    try:
                        json_data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    current_log_name = json_data.get('record', {}).get('name')
                    current_log_id = (
                        json_data.get('record', {})
                        .get('extra', {})
                        .get('uuid')
                    )
                    current_student_login = (
                        json_data.get('record', {})
                        .get('extra', {})
                        .get('student', {})
                        .get('contest_login')
                    )
                    if log_id and current_log_id != log_id:
                        continue
                    if (
                        student_login
                        and current_student_login != student_login
                    ):
                        continue
                    if log_name and current_log_name != log_name:
                        continue
                    response.items.append(json_data)
                    response.count += 1
                    if len(response.items) > last:
                        response.items = response.items[
                            -last:
                        ]  # TODO: optimize
                        response.count = len(response.items)
                break
        except UnicodeDecodeError:
            continue
    return response

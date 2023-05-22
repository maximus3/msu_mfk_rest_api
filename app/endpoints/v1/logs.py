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
    path: str | None = None,
    log_filters: list[logs_schemas.LogFilter] | None = None,
    log_file: str = 'app',
) -> logs_schemas.LogsResponse:
    settings = get_settings()
    log_filters = log_filters or []
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

                    record = json_data.get('record', {})
                    extra = record.get('extra', {})

                    current_log_id = (
                        extra
                        .get('uuid')
                    )
                    if log_id and current_log_id != log_id:
                        continue

                    current_student_login = (
                        extra
                        .get('student', {})
                        .get('contest_login')
                    )
                    if (
                        student_login
                        and current_student_login != student_login
                    ):
                        continue

                    current_log_name = record.get('name')
                    if log_name and current_log_name != log_name:
                        continue

                    current_log_path = (
                        extra
                        .get('request', {})
                        .get('path')
                    )
                    if path and current_log_path != path:
                        continue

                    all_filters_ok = True
                    for log_filter in log_filters:
                        value = record
                        for current_path in log_filter.json_path.split('.'):
                            if not value:
                                value = {}
                            value = value.get(current_path)
                        all_filters_ok = all_filters_ok or value == log_filter.value
                    if not all_filters_ok:
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

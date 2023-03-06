import logging
import sys
import typing as tp
import uuid

import loguru
import slowapi
import slowapi.errors as slowapi_errors
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from uvicorn.protocols import utils

from app.config import DefaultSettings, get_settings
from app.database.admin.creator import get_sqladmin
from app.endpoints import list_of_routes
from app.limiter import limiter


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


class UniqueIDMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: tp.Any) -> Response:
        # do something with the request object, for example
        request.scope['request_id'] = uuid.uuid4().hex
        # process the request and get the response
        response = Response(status_code=500)
        try:
            response = await call_next(request)
        except Exception as exc:
            raise exc
        finally:
            request_info_dict = {
                'request': {
                    'id': request['request_id'],
                    'method': request.method,
                    'scheme': request['scheme'],
                    'http_version': request['http_version'],
                    'path': utils.get_path_with_query_string(request.scope),
                    'status_code': response.status_code,
                    'client': utils.get_client_addr(request.scope),
                },
                'uuid': request['request_id'],
            }
            response.headers['log_id'] = request['request_id']
            contest_login = request.headers.get(
                'log_contest_login'
            ) or response.headers.get('log_contest_login')
            if contest_login:
                request_info_dict.update(
                    {
                        'student': {
                            'contest_login': contest_login,
                        }
                    }
                )
            with loguru.logger.contextualize(**request_info_dict):
                loguru.logger.info(
                    '{request[client]} - "{request[method]} {request[path]} '
                    'HTTP/{request[http_version]}" {request[status_code]}',
                    request=request_info_dict['request'],
                )
        return response


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno  # type: ignore

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage().replace('{', r'{{').replace('}', r'}}'),
            extra={},
        )


def configure_logger(settings: DefaultSettings) -> None:
    loguru.logger.remove()
    loguru.logger.add(
        sink=sys.stderr, serialize=not settings.DEBUG, enqueue=True
    )
    loguru.logger.add(
        settings.LOGGING_APP_FILE,
        rotation='500 MB',
        serialize=True,
        enqueue=True,
    )
    logging.getLogger('sqlalchemy.engine').setLevel('INFO')


def get_app(set_up_logger: bool = True) -> FastAPI:
    """
    Creates application and all dependable objects.
    """
    description = 'Микросервис, реализующий REST API сервис'

    tags_metadata = [
        {
            'name': 'Application Health',
            'description': 'API health check.',
        },
    ]

    settings = get_settings()
    middleware = [
        Middleware(UniqueIDMiddleware),
    ]
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=description,
        docs_url='/swagger',
        openapi_url='/openapi',
        version='0.1.0',
        openapi_tags=tags_metadata,
        middleware=middleware,
    )

    bind_routes(application, settings)
    add_pagination(application)
    application.state.settings = settings

    if set_up_logger:
        configure_logger(settings)

    _ = get_sqladmin(application)

    application.state.limiter = limiter
    application.add_exception_handler(
        slowapi_errors.RateLimitExceeded,
        slowapi._rate_limit_exceeded_handler,  # pylint: disable=protected-access
    )

    return application

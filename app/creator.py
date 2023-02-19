import logging
import sys
import uuid

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from loguru import logger
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from uvicorn.protocols import utils

from app.config import DefaultSettings, get_settings
from app.endpoints import list_of_routes


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


class UniqueIDMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
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
                }
            }
            with logger.contextualize(**request_info_dict):
                logger.info(
                    '{request[client]} - "{request[method]} {request[path]} HTTP/{request[http_version]}" {request[status_code]}',
                    request=request_info_dict['request'],
                )
        return response


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage(), extra={}
        )


def get_app() -> FastAPI:
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

    logger.remove()
    logger.add(sink=sys.stderr, serialize=True, enqueue=True)
    logging.getLogger('sqlalchemy.engine').setLevel('INFO')

    return application

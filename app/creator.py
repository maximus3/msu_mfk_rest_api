import logging
import uuid

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

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
        request.scope['request_id'] = uuid.uuid4()
        # process the request and get the response
        response = await call_next(request)
        return response


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

    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.log_obj_id = "default_id"
        return record

    logging.setLogRecordFactory(record_factory)

    return application

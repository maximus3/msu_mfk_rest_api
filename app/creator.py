import logging

from aiomisc.log import basic_config
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.config import DefaultSettings, get_settings
from app.endpoints import list_of_routes


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


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

    application = FastAPI(
        title='Scouts API',
        description=description,
        docs_url='/swagger',
        openapi_url='/openapi',
        version='0.1.0',
        openapi_tags=tags_metadata,
    )
    settings = get_settings()
    bind_routes(application, settings)
    add_pagination(application)
    application.state.settings = settings

    basic_config(
        format=settings.LOGGING_FORMAT,
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        filename='app.log',
        buffered=True,
    )

    return application

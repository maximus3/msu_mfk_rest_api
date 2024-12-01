import asyncio
import traceback

import asyncpg.exceptions
import loguru
import sqlalchemy.exc
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from uvicorn import run

from app.bot_helper import send
from app.config import get_settings
from app.creator import get_app
from app.utils.common import get_hostname


app = get_app()


@app.exception_handler(Exception)
async def exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:  # pragma: no cover
    response = JSONResponse(
        status_code=500,
        content={'message': 'Internal server error'},
    )
    settings = get_settings()
    message_list = [
        f'*Exception occurred on {settings.PROJECT_NAME}*:',
        'REQUEST:',
    ]
    for key, value in request.items():
        message_list.append(f'\t- {key}: {value}')
    message_list.extend(
        [
            '',
            f'EXCEPTION: {exc}',
        ]
    )
    if isinstance(
        exc,
        (
            asyncpg.exceptions.TooManyConnectionsError,
            sqlalchemy.exc.TimeoutError,
        ),
    ):
        response = JSONResponse(
            status_code=429,
            content={'message': 'Too many requests'},
        )
    else:
        await send.send_traceback_message_safe(
            logger=loguru.logger,
            message='\n'.join(message_list),
            code=traceback.format_exc(),
        )
    return response


if __name__ == '__main__':  # pragma: no cover
    settings_for_application = get_settings()

    asyncio.get_event_loop().run_until_complete(
        send.send_message_safe(
            logger=loguru.logger,
            message=f'Created application: '
            f'debug={settings_for_application.DEBUG}',
            level='info',
        )
    )

    run(
        'app.__main__:app',
        host=get_hostname(settings_for_application.APP_HOST),
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=['app'],
        log_level='debug' if settings_for_application.DEBUG else 'info',
        log_config='log.ini',
        access_log=False,
        forwarded_allow_ips='*',
        proxy_headers=True,
    )

import traceback

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from uvicorn import run

from app.bot_helper import send_error_message
from app.config import get_settings
from app.creator import get_app
from app.utils.common import get_hostname


app = get_app()


@app.exception_handler(Exception)
async def exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:  # pragma: no cover
    settings = get_settings()
    message_list = [
        f'*Exception occurred on {settings.PROJECT_NAME}*:',
        'REQUEST:',
    ]
    for key, value in request.items():
        message_list.append(f'\t- {key}: {value}')
    message_list.extend(
        ['', f'EXCEPTION: {exc}', '', f'{traceback.format_exc()}']
    )
    await send_error_message(
        message='\n'.join(message_list),
    )
    return JSONResponse(
        status_code=500,
        content={'message': 'Internal server error'},
    )


if __name__ == '__main__':  # pragma: no cover
    settings_for_application = get_settings()
    run(
        'app.__main__:app',
        host=get_hostname(settings_for_application.APP_HOST),
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=['app', 'tests'],
        log_level='debug' if settings_for_application.DEBUG else 'info',
        log_config='log.ini',
    )

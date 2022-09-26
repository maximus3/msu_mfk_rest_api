from uvicorn import run

from app.config import get_settings
from app.creator import get_app
from app.utils.common import get_hostname


app = get_app()

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

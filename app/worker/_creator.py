import celery

from app import config


def get_celery() -> celery.Celery:
    settings = config.get_settings()
    _celery = celery.Celery(__name__)
    _celery.conf.broker_url = settings.CELERY_BROKER_URL
    _celery.conf.result_backend = settings.CELERY_RESULT_BACKEND
    return _celery

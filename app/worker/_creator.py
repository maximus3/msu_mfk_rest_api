import asyncio
import functools
import traceback

import celery
import loguru

from app import config
from app.bot_helper import send


def get_celery() -> celery.Celery:
    settings = config.get_settings()
    _celery = celery.Celery(__name__)
    _celery.conf.broker_url = settings.CELERY_BROKER_URL
    _celery.conf.result_backend = settings.CELERY_RESULT_BACKEND
    return _celery


def async_to_sync(func):  # type: ignore
    @functools.wraps(func)
    def wrapped(*args, **kwargs):  # type: ignore
        return asyncio.run(func(*args, **kwargs))

    return wrapped


def task_wrapper(func):  # type: ignore
    @functools.wraps(func)
    async def _wrapped(  # type: ignore
        base_logger: 'loguru.Logger', *args, **kwargs
    ):
        base_logger.info(
            'Task started (args={}, kwargs={})',
            args,
            kwargs,
        )

        try:
            result = await func(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            base_logger.exception('Error in task: {}', exc)
            await send.send_traceback_message_safe(
                logger=base_logger,
                message='Error in task',
                code=traceback.format_exc(),
            )
            raise
        base_logger.info('Task finished')

        return result

    return _wrapped

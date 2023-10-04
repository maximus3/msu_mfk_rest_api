# pylint: disable=duplicate-code

import asyncio
import functools
import sys
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

    loguru.logger.remove()
    loguru.logger.add(sink=sys.stderr, serialize=True, enqueue=True)
    loguru.logger.add(
        settings.LOGGING_WORKER_FILE,
        rotation='500 MB',
        serialize=True,
        enqueue=True,
    )

    return _celery


def async_to_sync(func):  # type: ignore
    @functools.wraps(func)
    def wrapped(*args, **kwargs):  # type: ignore
        return asyncio.run(func(*args, **kwargs))

    return wrapped


def task_wrapper(func):  # type: ignore
    @functools.wraps(func)
    async def _wrapped(request_id: str, *args, **kwargs):  # type: ignore
        # settings = config.get_settings()
        # log_file_name = (
        #         settings.LOGGING_FILE_DIR
        #         / f'worker/task-{request_id}.log'
        # )
        base_logger = loguru.logger.bind(uuid=request_id)
        base_logger.info(
            'Task started (args={}, kwargs={})',
            args,
            kwargs,
        )

        kwargs.update(base_logger=base_logger)
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

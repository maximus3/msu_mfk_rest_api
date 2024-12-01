# pylint: disable=duplicate-code

import asyncio
import functools
import traceback

import celery
import loguru

from app import config, logger_config
from app.bot_helper import send
from app.database.connection import SessionManager
from app.logger_config import custom_loki_logger_handler


def get_celery() -> celery.Celery:
    settings = config.get_settings()
    logger_config.configure_logger(
        settings, log_file=settings.LOGGING_WORKER_FILE, application='worker'
    )

    _celery = celery.Celery(__name__)
    _celery.conf.broker_url = settings.CELERY_BROKER_URL
    _celery.conf.result_backend = settings.CELERY_RESULT_BACKEND
    SessionManager()

    return _celery


def async_to_sync(func):  # type: ignore
    @functools.wraps(func)
    def wrapped(*args, **kwargs):  # type: ignore
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(func(*args, **kwargs))

    return wrapped


def task_wrapper(func):  # type: ignore
    @functools.wraps(func)
    async def _wrapped(task, parent_id: str, *args, **kwargs):  # type: ignore
        # settings = config.get_settings()
        # log_file_name = (
        #         settings.LOGGING_FILE_DIR
        #         / f'worker/task-{request_id}.log'
        # )
        base_logger = loguru.logger.bind(
            parent_id=parent_id,
            uuid=task.request.id,
            celery_task={'name': task.name, 'id': task.request.id},
        )
        settings = config.get_settings()
        base_logger.add(
            sink=custom_loki_logger_handler.CustomLokiLoggerHandler(
                url='http://loki:3100/loki/api/v1/push',
                labels={
                    'application': 'worker',
                    'environment': settings.ENV,
                    'log_type': 'log',  # default
                },
                label_keys=logger_config.LABEL_KEYS,
                timeout=10,
                default_formatter=custom_loki_logger_handler.CustomLoguruFormatter(),
            ),
            serialize=True,
        )
        base_logger.info(
            'Task started (args={}, kwargs={})',
            args,
            kwargs,
        )

        kwargs.update(base_logger=base_logger)
        try:
            result = await func(self=task, *args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            base_logger.exception('Error in task: {}', exc)
            await send.send_traceback_message_safe(
                logger=base_logger,
                message=f'Error in task, parent_id={parent_id}',
                code=traceback.format_exc(),
            )
            raise
        base_logger.info('Task finished')

        return result

    return _wrapped

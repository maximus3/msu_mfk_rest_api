import logging
import pathlib
import sys

import loguru

from app import config, constants

from . import custom_loki_logger_handler


LABEL_KEYS = {
    'function',
    'name',
    'level',
    'uuid',
    'parent_id',
    'log_type',
    'request_path',
    'response_status_code',
    'course_id',
    'course_short_name',
    'contest_id',
    'contest_yandex_contest_id',
    'task_id',
    'task_yandex_task_id',
    'student_id',
    'student_contest_login',
    'group_id',
    'group_name',
    'group_yandex_group_id',
    'submission_id',
    'submission_run_id',
    'celery_task_id',
    'celery_task_name',
    'job_name',
}


def configure_logger(
    settings: config.DefaultSettings,
    log_file: pathlib.Path,
    application: str,
) -> None:  # pragma: no cover
    loguru.logger.remove()
    loguru.logger.add(
        sink=sys.stderr, serialize=not settings.DEBUG, enqueue=True
    )
    loguru.logger.add(
        log_file,
        **constants.LOGGER_PARAMS,  # type: ignore
    )
    loguru.logger.add(
        sink=custom_loki_logger_handler.CustomLokiLoggerHandler(
            url=settings.LOKI_PUSH_URL,
            labels={
                'application': application,
                'environment': settings.ENV,
                'log_type': 'log',  # default
            },
            label_keys=LABEL_KEYS,
            timeout=10,
            default_formatter=custom_loki_logger_handler.CustomLoguruFormatter(),
        ),
        serialize=True,
    )
    logging.getLogger('sqlalchemy.engine').setLevel('INFO')

import asyncio
import functools
import pathlib
import sys
import traceback
import uuid
from datetime import datetime

import loguru
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot_helper import send
from app.config import get_settings
from app.scheduler import list_of_jobs
from app.schemas import scheduler as scheduler_schemas


def _job_info_wrapper(  # pylint: disable=too-many-statements
    job_info: scheduler_schemas.JobInfo,
) -> scheduler_schemas.JobInfo:
    config = job_info.config or scheduler_schemas.JobConfig(send_logs=False)
    job_info.config = None

    def _job_wrapper(func):  # type: ignore
        @functools.wraps(func)
        async def _wrapped(*args, **kwargs):  # type: ignore
            log_id = uuid.uuid4().hex
            log_file_name = (
                settings.LOGGING_FILE_DIR
                / f'scheduler/job-{job_info.name}-{log_id}.log'
            )
            base_logger = loguru.logger.bind(uuid=log_id)
            if config.send_logs:
                handler_id = base_logger.add(
                    log_file_name,
                    serialize=True,
                    enqueue=True,
                    filter=lambda record: record['extra'].get('uuid')
                    == log_id,
                )
                await send.send_message_safe(
                    logger=base_logger,
                    message=f'Job {job_info.name} started '
                    f'(log_id={log_id})',
                    level='info',
                    chat_id=get_settings().TG_LOG_SEND_CHAT_ID,
                )

            base_logger.info(
                'Job {} started (args={}, kwargs={})',
                job_info.name,
                args,
                kwargs,
            )
            kwargs.update(base_logger=base_logger)
            try:
                result = await func(*args, **kwargs)
            except Exception as exc:  # pylint: disable=broad-except
                base_logger.exception(
                    'Error in job {}: {}', job_info.name, exc
                )
                await send.send_traceback_message_safe(
                    logger=base_logger,
                    message=f'Error in job {job_info.name}',
                    code=traceback.format_exc(),
                )
                raise
            base_logger.info('Job {} finished', job_info.name)

            if not config.send_logs:
                return result

            await send.send_message_safe(
                logger=base_logger,
                message=f'Job {job_info.name} finished (log_id={log_id})',
                level='info',
                chat_id=get_settings().TG_LOG_SEND_CHAT_ID,
            )

            base_logger.remove(handler_id)

            try:
                await send.send_file(
                    log_file_name,
                    f'job-{job_info.name}-{log_id}',
                    chat_id=settings.TG_LOG_SEND_CHAT_ID,
                )
            except Exception as send_exc:  # pylint: disable=broad-except
                base_logger.exception(
                    'Error while sending log file: {}', send_exc
                )
                await send.send_traceback_message_safe(
                    logger=base_logger,
                    message=f'Error while sending log file: {send_exc}',
                    code=traceback.format_exc(),
                )

            try:
                pathlib.Path(log_file_name).unlink()
            except Exception as exc:  # pylint: disable=broad-except
                base_logger.exception('Error while deleting log file: {}', exc)
                await send.send_traceback_message_safe(
                    logger=base_logger,
                    message=f'Error while deleting log file: {exc}',
                    code=traceback.format_exc(),
                )

            return result

        return _wrapped

    job_info.func = _job_wrapper(job_info.func)

    return job_info


def get_scheduler() -> AsyncIOScheduler:
    """
    Add scheduler jobs.
    """
    _scheduler = AsyncIOScheduler()
    for job_info in list_of_jobs:
        print(
            {
                k: v
                for k, v in _job_info_wrapper(job_info).dict().items()
                if v is not None
            }
        )
        _scheduler.add_job(
            **{
                k: v
                for k, v in _job_info_wrapper(job_info).dict().items()
                if v is not None
            }
        )
    return _scheduler


if __name__ == '__main__':
    settings = get_settings()
    loguru.logger.remove()
    loguru.logger.add(sink=sys.stderr, serialize=True, enqueue=True)
    loguru.logger.add(
        settings.LOGGING_SCHEDULER_FILE,
        rotation='500 MB',
        serialize=True,
        enqueue=True,
    )
    scheduler = get_scheduler()
    for job in scheduler.get_jobs():
        job.modify(next_run_time=datetime.now())
    scheduler.start()
    try:
        loguru.logger.info('Starting scheduler')
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        loguru.logger.info('Scheduler stopped')

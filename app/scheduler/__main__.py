import asyncio
import sys
from datetime import datetime

import loguru
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.scheduler import list_of_jobs


def get_scheduler() -> AsyncIOScheduler:
    """
    Add scheduler jobs.
    """
    _scheduler = AsyncIOScheduler()
    for job_info in list_of_jobs:
        _scheduler.add_job(
            **{k: v for k, v in job_info.dict().items() if v is not None}
        )
    return _scheduler


if __name__ == '__main__':
    settings = get_settings()
    scheduler = get_scheduler()
    for job in scheduler.get_jobs():
        job.modify(next_run_time=datetime.now())
    scheduler.start()
    loguru.logger.remove()
    loguru.logger.add(sink=sys.stderr, serialize=True, enqueue=True)
    loguru.logger.add(
        settings.LOGGING_SCHEDULER_FILE,
        rotation='500 MB',
        serialize=True,
        enqueue=True,
    )
    try:
        loguru.logger.info('Starting scheduler')
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        loguru.logger.info('Scheduler stopped')

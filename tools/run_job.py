import asyncio

from loguru import logger


try:
    from app.scheduler import list_of_jobs
except ImportError:
    logger.warning('No jobs found')
    list_of_jobs = []


def main(job_name: str) -> None:
    jobs = list(
        filter(lambda job_info: job_info.name == job_name, list_of_jobs)
    )
    if len(jobs) == 0:
        logger.error('Job {} not found', job_name)
        return
    if len(jobs) > 1:
        logger.error('Job {} is not unique', job_name)
        return
    job = jobs[0]
    asyncio.run(job.func(base_logger=logger))

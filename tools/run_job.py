import asyncio
import logging

from app.scheduler import list_of_jobs


def main(job_name):
    logger = logging.getLogger(__name__)
    jobs = list(
        filter(lambda job_info: job_info['name'] == job_name, list_of_jobs)
    )
    if len(jobs) == 0:
        logger.error('Job %s not found', job_name)
        return
    if len(jobs) > 1:
        logger.error('Job %s is not unique', job_name)
        return
    job = jobs[0]
    asyncio.run(job['func']())

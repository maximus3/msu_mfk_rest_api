from typing import Any

from app.scheduler.contest_register import (
    job_info as contest_register_job_info,
)


list_of_jobs: list[dict[str, Any]] = [
    contest_register_job_info,
]


__all__ = [
    'list_of_jobs',
]

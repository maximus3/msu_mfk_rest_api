from typing import Any

from .db_dump import job_info as dump_db_job_info


list_of_jobs: list[dict[str, Any]] = [
    dump_db_job_info,
]


__all__ = [
    'list_of_jobs',
]

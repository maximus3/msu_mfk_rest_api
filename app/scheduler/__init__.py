from typing import Any

from .contest_register import job_info as contest_register_job_info
from .db_dump import job_info as dump_db_job_info


list_of_jobs: list[dict[str, Any]] = [
    contest_register_job_info,
    dump_db_job_info,
]


__all__ = [
    'list_of_jobs',
]

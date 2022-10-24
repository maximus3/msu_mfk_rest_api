from typing import Any

from .contest_results import job_info as contest_results_job_info


list_of_jobs: list[dict[str, Any]] = [
    # contest_register_job_info,
    # dump_db_job_info,
    # ping_job_info,
    contest_results_job_info,
]


__all__ = [
    'list_of_jobs',
]

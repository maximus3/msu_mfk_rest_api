from typing import Any

from .contest_register import job_info as contest_register_job_info
from .contest_results import job_info as contest_results_job_info
from .contest_results_dump import job_info as contest_results_dump_job_info
from .db_dump import job_info as dump_db_job_info
from .ping import job_info as ping_job_info


list_of_jobs: list[dict[str, Any]] = [
    contest_register_job_info,
    dump_db_job_info,
    ping_job_info,
    contest_results_job_info,
    contest_results_dump_job_info,
]


__all__ = [
    'list_of_jobs',
]

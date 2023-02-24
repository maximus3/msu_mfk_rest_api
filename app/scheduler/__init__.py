from app.schemas import scheduler as scheduler_schemas

from .contest_register import job_info as contest_register_job_info
from .db_dump import job_info as dump_db_job_info
from .ping import job_info as ping_job_info


# from .update_results import job_info as update_student_results_job_info


list_of_jobs: list[scheduler_schemas.JobInfo] = [
    contest_register_job_info,
    dump_db_job_info,
    ping_job_info,
    # update_student_results_job_info,
]


__all__ = [
    'list_of_jobs',
]

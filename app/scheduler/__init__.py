# Code generated automatically.

from app.schemas import scheduler as scheduler_schemas

from .contest_register import job as contest_register
from .contest_register_group import job as contest_register_group
from .db_dump import job as db_dump
from .ping import job as ping
from .update_results import job as update_results


list_of_jobs: list[scheduler_schemas.JobInfo] = [
    scheduler_schemas.JobInfo(
        **{
            'trigger': 'interval',
            'minutes': 1,
            'config': {'send_logs': False},
        },
        func=ping,
        name='ping',
    ),
    scheduler_schemas.JobInfo(
        **{'trigger': 'cron', 'hour': 3, 'config': {'send_logs': True}},
        func=db_dump,
        name='db_dump',
    ),
    scheduler_schemas.JobInfo(
        **{
            'trigger': 'interval',
            'minutes': 10,
            'config': {'send_logs': True},
        },
        func=contest_register,
        name='contest_register',
    ),
    scheduler_schemas.JobInfo(
        **{
            'trigger': 'interval',
            'minutes': 10,
            'config': {'send_logs': True},
        },
        func=contest_register_group,
        name='contest_register_group',
    ),
    scheduler_schemas.JobInfo(
        **{'trigger': 'interval', 'hours': 1, 'config': {'send_logs': True}},
        func=update_results,
        name='update_results',
    ),
]


__all__ = [
    'list_of_jobs',
]

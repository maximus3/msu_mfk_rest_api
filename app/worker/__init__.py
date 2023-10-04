from ._creator import async_to_sync, get_celery, task_wrapper
from .get_results_by_course import task as get_results_by_course


celery_broker = get_celery()

get_results_by_course_task = celery_broker.task(name='get_results_by_course')(
    async_to_sync(task_wrapper(get_results_by_course))
)


__all__ = [
    'celery_broker',
    'get_results_by_course_task',
]

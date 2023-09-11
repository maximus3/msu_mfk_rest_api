from ._creator import get_celery
from .get_results_by_course import task as get_results_by_course


celery_broker = get_celery()

get_results_by_course_task = celery_broker.task(name='get_results_by_course')(
    get_results_by_course
)


__all__ = [
    'celery_broker',
    'get_results_by_course_task',
]

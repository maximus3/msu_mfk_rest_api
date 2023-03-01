# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class StudentTaskAdmin(ModelView, model=models.StudentTask):
    _column_list = [
        'id',
        'course_id',
        'contest_id',
        'task_id',
        'student_id',
        'final_score',
        'best_score_before_finish',
        'best_score_no_deadline',
        'is_done',
        'best_score_before_finish_submission_id',
        'best_score_no_deadline_submission_id',
    ]
    column_list = [
        'id',
        'course_id',
        'contest_id',
        'task_id',
        'student_id',
        'final_score',
        'best_score_before_finish',
        'best_score_no_deadline',
        'is_done',
        'best_score_before_finish_submission_id',
        'best_score_no_deadline_submission_id',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'StudentTasks'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(
        ['course', 'contest', 'task', 'student']
    )
    form_args = models_forms.get_form_args(
        ['course', 'contest', 'task', 'student']
    )

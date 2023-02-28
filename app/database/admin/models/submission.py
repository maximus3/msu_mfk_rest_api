# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class SubmissionAdmin(ModelView, model=models.Submission):
    _column_list = [
        'id',
        'course_id',
        'contest_id',
        'task_id',
        'student_id',
        'student_task_id',
        'author_id',
        'run_id',
        'verdict',
        'final_score',
        'score',
        'score_before_finish',
        'submission_link',
        'time_from_start',
        'submission_time',
    ]
    column_list = [
        'id',
        'course_id',
        'contest_id',
        'task_id',
        'student_id',
        'student_task_id',
        'author_id',
        'run_id',
        'verdict',
        'final_score',
        'score',
        'score_before_finish',
        'submission_link',
        'time_from_start',
        'submission_time',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Submissions'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(
        ['course', 'contest', 'task', 'student', 'student_task']
    )
    form_args = models_forms.get_form_args(
        ['course', 'contest', 'task', 'student', 'student_task']
    )

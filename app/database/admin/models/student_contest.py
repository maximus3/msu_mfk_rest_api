# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class StudentContestAdmin(ModelView, model=models.StudentContest):
    _column_list = [
        'id',
        'course_id',
        'contest_id',
        'student_id',
        'author_id',
        'tasks_done',
        'score',
        'score_no_deadline',
        'is_ok',
        'is_ok_no_deadline',
    ]
    column_list = [
        'id',
        'course_id',
        'contest_id',
        'student_id',
        'author_id',
        'tasks_done',
        'score',
        'score_no_deadline',
        'is_ok',
        'is_ok_no_deadline',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'StudentContests'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(
        ['course', 'contest', 'student']
    )
    form_args = models_forms.get_form_args(['course', 'contest', 'student'])

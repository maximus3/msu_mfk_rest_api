# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class StudentContestLevelsAdmin(ModelView, model=models.StudentContestLevels):
    _column_list = [
        'id',
        'course_id',
        'contest_id',
        'student_id',
        'contest_level_id',
        'is_ok',
    ]
    column_list = [
        'id',
        'course_id',
        'contest_id',
        'student_id',
        'contest_level_id',
        'is_ok',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'StudentContestLevelss'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(
        ['course', 'contest', 'student', 'contest_levels']
    )
    form_args = models_forms.get_form_args(
        ['course', 'contest', 'student', 'contest_levels']
    )

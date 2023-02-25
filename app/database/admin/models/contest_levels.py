# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class ContestLevelsAdmin(ModelView, model=models.ContestLevels):
    _column_list = [
        'id',
        'course_id',
        'contest_id',
        'level_name',
        'level_ok_method',
        'count_method',
        'ok_threshold',
        'include_after_deadline',
    ]
    column_list = [
        'id',
        'course_id',
        'contest_id',
        'level_name',
        'level_ok_method',
        'count_method',
        'ok_threshold',
        'include_after_deadline',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'ContestLevelss'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(['course', 'contest'])
    form_args = models_forms.get_form_args(['course', 'contest'])

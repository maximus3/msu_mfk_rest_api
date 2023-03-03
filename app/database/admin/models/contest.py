# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class ContestAdmin(ModelView, model=models.Contest):
    _column_list = [
        'id',
        'course_id',
        'yandex_contest_id',
        'deadline',
        'lecture',
        'link',
        'tasks_count',
        'score_max',
        'levels',
        'tags',
        'name_format',
        'default_final_score_evaluation_formula',
    ]
    column_list = [
        'id',
        'course_id',
        'yandex_contest_id',
        'deadline',
        'lecture',
        'link',
        'tasks_count',
        'score_max',
        'levels',
        'tags',
        'name_format',
        'default_final_score_evaluation_formula',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Contests'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(['course'])
    form_args = models_forms.get_form_args(['course'])

# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class TaskAdmin(ModelView, model=models.Task):
    _column_list = [
        'id',
        'contest_id',
        'yandex_task_id',
        'name',
        'alias',
        'is_zero_ok',
        'score_max',
    ]
    column_list = [
        'id',
        'contest_id',
        'yandex_task_id',
        'name',
        'alias',
        'is_zero_ok',
        'score_max',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Tasks'
    column_default_sort = 'contest_id'

    form_overrides = models_forms.get_form_overrides(['contest'])
    form_args = models_forms.get_form_args(['contest'])

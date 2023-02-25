# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class TQDMLogsAdmin(ModelView, model=models.TQDMLogs):
    _column_list = [
        'id',
        'name',
        'current',
        'total',
        'need_time',
        'need_time_for_all',
        'avg_data',
        'all_time',
    ]
    column_list = [
        'id',
        'name',
        'current',
        'total',
        'need_time',
        'need_time_for_all',
        'avg_data',
        'all_time',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'TQDMLogss'
    column_default_sort = 'name'

    form_overrides = models_forms.get_form_overrides([])
    form_args = models_forms.get_form_args([])

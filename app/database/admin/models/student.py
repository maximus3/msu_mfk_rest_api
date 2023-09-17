# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class StudentAdmin(ModelView, model=models.Student):
    _column_list = [
        'id',
        'fio',
        'contest_login',
        'tg_id',
        'tg_username',
        'bm_id',
        'token',
        'yandex_id',
    ]
    column_list = [
        'id',
        'fio',
        'contest_login',
        'tg_id',
        'tg_username',
        'bm_id',
        'token',
        'yandex_id',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Students'
    column_default_sort = 'fio'

    form_overrides = models_forms.get_form_overrides([])
    form_args = models_forms.get_form_args([])

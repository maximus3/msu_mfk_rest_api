# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class GroupAdmin(ModelView, model=models.Group):
    _column_list = ['id', 'name', 'yandex_group_id', 'course_id']
    column_list = ['id', 'name', 'yandex_group_id', 'course_id']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Groups'
    column_default_sort = 'name'

    form_overrides = models_forms.get_form_overrides(['course'])
    form_args = models_forms.get_form_args(['course'])

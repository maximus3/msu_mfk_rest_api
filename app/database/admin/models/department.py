# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class DepartmentAdmin(ModelView, model=models.Department):
    _column_list = ['id', 'name']
    column_list = ['id', 'name']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Departments'
    column_default_sort = 'name'

    form_overrides = models_forms.get_form_overrides([])
    form_args = models_forms.get_form_args([])

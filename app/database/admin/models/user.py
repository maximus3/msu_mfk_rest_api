# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class UserAdmin(ModelView, model=models.User):
    _column_list = ['id', 'username', 'password']
    column_list = ['id', 'username', 'password']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Users'
    column_default_sort = 'username'

    form_overrides = models_forms.get_form_overrides([])
    form_args = models_forms.get_form_args([])

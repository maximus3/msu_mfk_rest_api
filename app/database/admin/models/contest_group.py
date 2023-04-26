# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class ContestGroupAdmin(ModelView, model=models.ContestGroup):
    _column_list = ['id', 'group_id', 'contest_id']
    column_list = ['id', 'group_id', 'contest_id']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'ContestGroups'
    column_default_sort = 'group_id'

    form_overrides = models_forms.get_form_overrides(['group', 'contest'])
    form_args = models_forms.get_form_args(['group', 'contest'])

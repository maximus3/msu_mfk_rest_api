# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class StudentGroupAdmin(ModelView, model=models.StudentGroup):
    _column_list = ['id', 'group_id', 'student_id']
    column_list = ['id', 'group_id', 'student_id']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'StudentGroups'
    column_default_sort = 'group_id'

    form_overrides = models_forms.get_form_overrides(['group', 'student'])
    form_args = models_forms.get_form_args(['group', 'student'])

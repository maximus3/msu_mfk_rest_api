# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database.admin import models_forms
from app.database import models


class StudentDepartmentAdmin(ModelView, model=models.StudentDepartment):
    _column_list = ['id', 'student_id', 'department_id']
    column_list = ['id', 'student_id', 'department_id']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'StudentDepartments'
    column_default_sort = 'student_id'

    form_overrides = models_forms.get_form_overrides(['student', 'department'])
    form_args = models_forms.get_form_args(['student', 'department'])
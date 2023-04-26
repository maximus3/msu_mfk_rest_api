# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class CourseLevelsAdmin(ModelView, model=models.CourseLevels):
    _column_list = ['id', 'course_id', 'level_name', 'level_info']
    column_list = ['id', 'course_id', 'level_name', 'level_info']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'CourseLevelss'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(['course'])
    form_args = models_forms.get_form_args(['course'])

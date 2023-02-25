# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class StudentCourseLevelsAdmin(ModelView, model=models.StudentCourseLevels):
    _column_list = [
        'id',
        'course_id',
        'student_id',
        'course_level_id',
        'is_ok',
    ]
    column_list = ['id', 'course_id', 'student_id', 'course_level_id', 'is_ok']
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'StudentCourseLevelss'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(
        ['course', 'student', 'course_levels']
    )
    form_args = models_forms.get_form_args(
        ['course', 'student', 'course_levels']
    )

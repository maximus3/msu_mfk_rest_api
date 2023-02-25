# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class StudentCourseAdmin(ModelView, model=models.StudentCourse):
    _column_list = [
        'id',
        'course_id',
        'student_id',
        'score',
        'contests_ok',
        'score_percent',
        'contests_ok_percent',
        'is_ok',
        'is_ok_final',
    ]
    column_list = [
        'id',
        'course_id',
        'student_id',
        'score',
        'contests_ok',
        'score_percent',
        'contests_ok_percent',
        'is_ok',
        'is_ok_final',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'StudentCourses'
    column_default_sort = 'course_id'

    form_overrides = models_forms.get_form_overrides(['course', 'student'])
    form_args = models_forms.get_form_args(['course', 'student'])

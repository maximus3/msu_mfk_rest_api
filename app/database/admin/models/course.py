# Code generated automatically.
# pylint: disable=duplicate-code

from sqladmin import ModelView

from app.database import models
from app.database.admin import models_forms


class CourseAdmin(ModelView, model=models.Course):
    _column_list = [
        'id',
        'name',
        'short_name',
        'channel_link',
        'chat_link',
        'lk_link',
        'info',
        'need_info_from_students',
        'is_active',
        'is_open',
        'code_word',
        'is_open_registration',
        'register_start',
        'register_end',
        'score_max',
        'contest_count',
        'default_final_score_evaluation_formula',
        'is_archive',
        'have_early_exam',
    ]
    column_list = [
        'id',
        'name',
        'short_name',
        'channel_link',
        'chat_link',
        'lk_link',
        'info',
        'need_info_from_students',
        'is_active',
        'is_open',
        'code_word',
        'is_open_registration',
        'register_start',
        'register_end',
        'score_max',
        'contest_count',
        'default_final_score_evaluation_formula',
        'is_archive',
        'have_early_exam',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Courses'
    column_default_sort = 'name'

    form_overrides = models_forms.get_form_overrides([])
    form_args = models_forms.get_form_args([])

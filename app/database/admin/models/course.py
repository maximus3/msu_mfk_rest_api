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
        'score_max',
        'contest_count',
        'ok_method',
        'ok_threshold_perc',
        'default_update_on',
        'is_open_registration',
        'is_archive',
    ]
    column_list = [
        'id',
        'name',
        'short_name',
        'channel_link',
        'chat_link',
        'lk_link',
        'score_max',
        'contest_count',
        'ok_method',
        'ok_threshold_perc',
        'default_update_on',
        'is_open_registration',
        'is_archive',
    ]
    form_excluded_columns = ['id', 'dt_created', 'dt_updated']
    form_include_pk = True
    name_plural = 'Courses'
    column_default_sort = 'name'

    form_overrides = models_forms.get_form_overrides([])
    form_args = models_forms.get_form_args([])

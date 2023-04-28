# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import CourseLevels


class CourseLevelsFactory(Factory):
    class Meta:
        model = CourseLevels

    course_id = Faker('uuid4')
    level_name = fuzzy.FuzzyText()
    result_update_end = Faker('date_time')
    level_info = '{}'

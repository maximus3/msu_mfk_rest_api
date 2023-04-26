# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import CourseLevels


class CourseLevelsFactory(Factory):
    class Meta:
        model = CourseLevels

    course_id = Faker('uuid4')
    level_name = fuzzy.FuzzyText()
    level_ok_method = fuzzy.FuzzyText()
    contest_ok_level_name = fuzzy.FuzzyText()
    count_method = fuzzy.FuzzyText()
    ok_threshold = fuzzy.FuzzyFloat(0, 1)
    level_info = '{}'

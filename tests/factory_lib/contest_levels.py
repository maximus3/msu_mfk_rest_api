# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import ContestLevels


class ContestLevelsFactory(Factory):
    class Meta:
        model = ContestLevels

    course_id = Faker('uuid4')
    contest_id = Faker('uuid4')
    level_name = fuzzy.FuzzyText()
    level_ok_method = fuzzy.FuzzyText()
    count_method = fuzzy.FuzzyText()
    ok_threshold = fuzzy.FuzzyFloat(0, 1)
    include_after_deadline = fuzzy.FuzzyChoice([True, False])

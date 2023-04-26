# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import Group


class GroupFactory(Factory):
    class Meta:
        model = Group

    name = fuzzy.FuzzyText()
    yandex_group_id = fuzzy.FuzzyInteger(1, 10000)
    course_id = Faker('uuid4')

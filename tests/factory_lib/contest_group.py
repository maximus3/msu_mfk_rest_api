# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker

from app.database.models import ContestGroup


class ContestGroupFactory(Factory):
    class Meta:
        model = ContestGroup

    group_id = Faker('uuid4')
    contest_id = Faker('uuid4')

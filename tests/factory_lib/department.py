# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, fuzzy

from app.database.models import Department


class DepartmentFactory(Factory):
    class Meta:
        model = Department

    name = fuzzy.FuzzyText()

# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, fuzzy

from app.database.models import User


class UserFactory(Factory):
    class Meta:
        model = User

    username = fuzzy.FuzzyText()
    password = fuzzy.FuzzyText()

from factory import Factory, fuzzy

from app.database.models import User


class UserFactory(Factory):
    class Meta:
        model = User

    username = fuzzy.FuzzyText(length=10)
    password = fuzzy.FuzzyText(length=10)

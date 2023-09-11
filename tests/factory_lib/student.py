# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, fuzzy

from app.database.models import Student


class StudentFactory(Factory):
    class Meta:
        model = Student

    fio = fuzzy.FuzzyText()
    contest_login = fuzzy.FuzzyText()
    tg_id = fuzzy.FuzzyText()
    tg_username = fuzzy.FuzzyText()
    bm_id = fuzzy.FuzzyText()
    token = fuzzy.FuzzyText()

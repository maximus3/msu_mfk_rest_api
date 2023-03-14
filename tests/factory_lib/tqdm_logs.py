# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, fuzzy

from app.database.models import TQDMLogs


class TQDMLogsFactory(Factory):
    class Meta:
        model = TQDMLogs

    name = fuzzy.FuzzyText()
    current = fuzzy.FuzzyInteger(1, 100)
    total = fuzzy.FuzzyInteger(1, 100)
    need_time = fuzzy.FuzzyText()
    need_time_for_all = fuzzy.FuzzyText()
    avg_data = fuzzy.FuzzyText()
    all_time = fuzzy.FuzzyText()

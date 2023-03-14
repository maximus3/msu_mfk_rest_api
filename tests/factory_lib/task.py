# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import Task


class TaskFactory(Factory):
    class Meta:
        model = Task

    contest_id = Faker('uuid4')
    yandex_task_id = fuzzy.FuzzyText()
    name = fuzzy.FuzzyText()
    alias = fuzzy.FuzzyText()
    is_zero_ok = fuzzy.FuzzyChoice([True, False])
    score_max = fuzzy.FuzzyFloat(0, 1)
    final_score_evaluation_formula = fuzzy.FuzzyText()

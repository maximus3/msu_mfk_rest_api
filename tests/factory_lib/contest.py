# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import Contest


class ContestFactory(Factory):
    class Meta:
        model = Contest

    course_id = Faker('uuid4')
    yandex_contest_id = fuzzy.FuzzyInteger(1, 10000)
    deadline = Faker('date_time')
    lecture = fuzzy.FuzzyInteger(1, 10000)
    link = fuzzy.FuzzyText()
    tasks_count = fuzzy.FuzzyInteger(1, 10000)
    score_max = fuzzy.FuzzyFloat(0, 1)
    tags = []  # type: ignore
    name_format = fuzzy.FuzzyText()
    default_final_score_evaluation_formula = fuzzy.FuzzyText()

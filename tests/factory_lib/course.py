# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import Course


class CourseFactory(Factory):
    class Meta:
        model = Course

    name = fuzzy.FuzzyText()
    short_name = fuzzy.FuzzyText()
    channel_link = fuzzy.FuzzyText()
    chat_link = fuzzy.FuzzyText()
    lk_link = fuzzy.FuzzyText()
    info = fuzzy.FuzzyText(length=64)
    need_info_from_students = '{}'
    is_active = fuzzy.FuzzyChoice([True, False])
    is_open = fuzzy.FuzzyChoice([True, False])
    code_word = fuzzy.FuzzyText()
    is_open_registration = fuzzy.FuzzyChoice([True, False])
    register_start = Faker('date_time')
    register_end = Faker('date_time')
    score_max = fuzzy.FuzzyFloat(0, 1)
    contest_count = fuzzy.FuzzyInteger(1, 10000)
    default_final_score_evaluation_formula = fuzzy.FuzzyText()
    is_archive = fuzzy.FuzzyChoice([True, False])

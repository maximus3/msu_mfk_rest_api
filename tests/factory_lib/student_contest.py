# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import StudentContest


class StudentContestFactory(Factory):
    class Meta:
        model = StudentContest

    course_id = Faker('uuid4')
    contest_id = Faker('uuid4')
    student_id = Faker('uuid4')
    author_id = fuzzy.FuzzyInteger(1, 10000)
    tasks_done = fuzzy.FuzzyInteger(1, 10000)
    score = fuzzy.FuzzyFloat(0, 1)
    score_no_deadline = fuzzy.FuzzyFloat(0, 1)
    is_ok = fuzzy.FuzzyChoice([True, False])
    is_ok_no_deadline = fuzzy.FuzzyChoice([True, False])

# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import Submission


class SubmissionFactory(Factory):
    class Meta:
        model = Submission

    course_id = Faker('uuid4')
    contest_id = Faker('uuid4')
    task_id = Faker('uuid4')
    student_id = Faker('uuid4')
    student_task_id = Faker('uuid4')
    author_id = fuzzy.FuzzyInteger(1, 100)
    run_id = fuzzy.FuzzyInteger(1, 100)
    verdict = fuzzy.FuzzyText()
    final_score = fuzzy.FuzzyFloat(0, 1)
    score_no_deadline = fuzzy.FuzzyFloat(0, 1)
    score_before_finish = fuzzy.FuzzyFloat(0, 1)
    submission_link = fuzzy.FuzzyText()
    submission_time = Faker('date_time')

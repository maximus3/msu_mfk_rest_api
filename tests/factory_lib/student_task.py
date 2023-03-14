# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import StudentTask


class StudentTaskFactory(Factory):
    class Meta:
        model = StudentTask

    course_id = Faker('uuid4')
    contest_id = Faker('uuid4')
    task_id = Faker('uuid4')
    student_id = Faker('uuid4')
    final_score = fuzzy.FuzzyFloat(0, 1)
    best_score_before_finish = fuzzy.FuzzyFloat(0, 1)
    best_score_no_deadline = fuzzy.FuzzyFloat(0, 1)
    is_done = fuzzy.FuzzyChoice([True, False])
    best_score_before_finish_submission_id = Faker('uuid4')
    best_score_no_deadline_submission_id = Faker('uuid4')

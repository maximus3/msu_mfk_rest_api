# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import StudentContestLevels


class StudentContestLevelsFactory(Factory):
    class Meta:
        model = StudentContestLevels

    course_id = Faker('uuid4')
    contest_id = Faker('uuid4')
    student_id = Faker('uuid4')
    contest_level_id = Faker('uuid4')
    is_ok = fuzzy.FuzzyChoice([True, False])

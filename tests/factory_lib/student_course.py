# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import StudentCourse


class StudentCourseFactory(Factory):
    class Meta:
        model = StudentCourse

    course_id = Faker('uuid4')
    student_id = Faker('uuid4')
    score = fuzzy.FuzzyFloat(0, 1)
    score_no_deadline = fuzzy.FuzzyFloat(0, 1)
    contests_ok = fuzzy.FuzzyInteger(1, 10000)
    is_ok = fuzzy.FuzzyChoice([True, False])
    is_ok_final = fuzzy.FuzzyChoice([True, False])

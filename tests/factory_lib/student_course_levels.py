# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker, fuzzy

from app.database.models import StudentCourseLevels


class StudentCourseLevelsFactory(Factory):
    class Meta:
        model = StudentCourseLevels

    course_id = Faker('uuid4')
    student_id = Faker('uuid4')
    course_level_id = Faker('uuid4')
    is_ok = fuzzy.FuzzyChoice([True, False])

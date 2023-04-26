# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker

from app.database.models import StudentGroup


class StudentGroupFactory(Factory):
    class Meta:
        model = StudentGroup

    group_id = Faker('uuid4')
    student_id = Faker('uuid4')

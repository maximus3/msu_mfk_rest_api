# Code generated automatically.
# pylint: disable=duplicate-code

from factory import Factory, Faker

from app.database.models import StudentDepartment


class StudentDepartmentFactory(Factory):
    class Meta:
        model = StudentDepartment

    student_id = Faker('uuid4')
    department_id = Faker('uuid4')

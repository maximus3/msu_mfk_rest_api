from factory import Factory, Faker, fuzzy

from app.database.models import (
    Contest,
    Course,
    Department,
    Student,
    StudentContest,
    StudentCourse,
    StudentDepartment,
    User,
)


class UserFactory(Factory):
    class Meta:
        model = User

    username = fuzzy.FuzzyText(length=10)
    password = fuzzy.FuzzyText(length=10)


class CourseFactory(Factory):
    class Meta:
        model = Course

    name = fuzzy.FuzzyText(length=20)
    short_name = fuzzy.FuzzyText(length=10)
    channel_link = fuzzy.FuzzyText(length=10, prefix='https://')
    chat_link = fuzzy.FuzzyText(length=10, prefix='https://')
    lk_link = fuzzy.FuzzyText(length=10, prefix='https://')


class DepartmentFactory(Factory):
    class Meta:
        model = Department

    name = fuzzy.FuzzyText(length=20)


class StudentFactory(Factory):
    class Meta:
        model = Student

    fio = Faker('name')
    contest_login = fuzzy.FuzzyText(length=10)
    token = fuzzy.FuzzyText(length=64)


class ContestFactory(Factory):
    class Meta:
        model = Contest

    course_id = Faker('uuid4')
    deadline = Faker('date_time')
    lecture = fuzzy.FuzzyInteger(1, 10)
    link = fuzzy.FuzzyText(length=10, prefix='https://')
    tasks_count = fuzzy.FuzzyInteger(1, 10)
    score_max = fuzzy.FuzzyInteger(1, 10)
    levels = {'count': 1, 'levels': [{'name': 'level1', 'score_need': 1}]}
    is_necessary = fuzzy.FuzzyChoice([True, False])
    yandex_contest_id = fuzzy.FuzzyInteger(30000, 40000)


class StudentCourseFactory(Factory):
    class Meta:
        model = StudentCourse

    course_id = Faker('uuid4')
    student_id = Faker('uuid4')


class StudentContestFactory(Factory):
    class Meta:
        model = StudentContest

    course_id = Faker('uuid4')
    contest_id = Faker('uuid4')
    student_id = Faker('uuid4')
    tasks_done = fuzzy.FuzzyInteger(1, 10)
    score = fuzzy.FuzzyInteger(1, 10)
    is_ok = fuzzy.FuzzyChoice([True, False])


class StudentDepartmentFactory(Factory):
    class Meta:
        model = StudentDepartment

    student_id = Faker('uuid4')
    department_id = Faker('uuid4')

from factory import Factory, Faker, fuzzy

from app.database import models
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
    is_open_registration = True
    is_archive = False


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
    tags = ['NECESSARY']
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
    author_id = fuzzy.FuzzyInteger(1, 1000)


class StudentDepartmentFactory(Factory):
    class Meta:
        model = StudentDepartment

    student_id = Faker('uuid4')
    department_id = Faker('uuid4')


class TaskFactory(Factory):
    class Meta:
        model = models.Task

    contest_id = Faker('uuid4')
    yandex_task_id = fuzzy.FuzzyText()
    name = fuzzy.FuzzyText()
    alias = fuzzy.FuzzyText()
    is_zero_ok = fuzzy.FuzzyChoice([True, False])
    score_max = fuzzy.FuzzyInteger(1, 10)


class ContestLevelsFactory(Factory):
    class Meta:
        model = models.ContestLevels

    contest_id = Faker('uuid4')
    course_id = Faker('uuid4')
    level_name = fuzzy.FuzzyText()
    level_ok_method = fuzzy.FuzzyText()
    count_method = fuzzy.FuzzyText()
    ok_threshold = fuzzy.FuzzyInteger(1, 100)
    include_after_deadline = fuzzy.FuzzyChoice([True, False])


class StudentTaskFactory(Factory):
    class Meta:
        model = models.StudentTask

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


class SubmissionFactory(Factory):
    class Meta:
        model = models.Submission

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
    time_from_start = fuzzy.FuzzyInteger(1, 100)
    submission_time = Faker('date_time')

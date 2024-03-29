# pylint: disable=unused-argument,too-many-lines
import typing

import sqlalchemy as sa
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class Student(BaseModel):
    """
    Student model in database.
    """

    __tablename__ = 'student'

    fio = sa.Column(sa.String, nullable=False)
    contest_login = sa.Column(sa.String, unique=True, nullable=False)
    tg_id = sa.Column(
        sa.String, unique=True, nullable=False, doc='Telegram ID'
    )
    tg_username = sa.Column(sa.String, nullable=True, doc='Telegram Username')
    bm_id = sa.Column(
        sa.String, unique=True, nullable=False, doc='Bot Mother ID'
    )
    token = sa.Column(sa.String, unique=True, nullable=False)
    yandex_id = sa.Column(sa.String, unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint(
            'char_length(contest_login) > 0', name='contest_login_min_length'
        ),
        CheckConstraint('char_length(tg_id) > 0', name='tg_id_min_length'),
        CheckConstraint('char_length(bm_id) > 0', name='bm_id_min_length'),
        CheckConstraint('char_length(token) > 0', name='token_min_length'),
        CheckConstraint(
            'char_length(yandex_id) > 0', name='yandex_id_min_length'
        ),
    )

    @sa.orm.validates('contest_login')
    def validate_contest_login(
        self, key: typing.Any, contest_login: str
    ) -> str:
        if not contest_login:
            raise ValueError('contest_login too short')
        return contest_login

    @sa.orm.validates('tg_id')
    def validate_tg_id(self, key: typing.Any, tg_id: str) -> str:
        if not tg_id:
            raise ValueError('tg_id too short')
        return tg_id

    @sa.orm.validates('bm_id')
    def validate_bm_id(self, key: typing.Any, bm_id: str) -> str:
        if not bm_id:
            raise ValueError('bm_id too short')
        return bm_id

    @sa.orm.validates('token')
    def validate_token(self, key: typing.Any, token: str) -> str:
        if not token:
            raise ValueError('token too short')
        return token

    @sa.orm.validates('yandex_id')
    def validate_yandex_id(self, key: typing.Any, yandex_id: str) -> str:
        if not yandex_id:
            raise ValueError('yandex_id too short')
        return yandex_id

    def __repr__(self):  # type: ignore
        return f'<Student {self.contest_login}>'


class StudentDepartment(BaseModel):
    """
    Relation between Student and Department.

    Many-to-one relation.
    """

    __tablename__ = 'student_department'

    student_id = sa.Column(
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    department_id = sa.Column(
        sa.ForeignKey('department.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    def __repr__(self):  # type: ignore
        return (
            f'<StudentDepartment student_id={self.student_id} '
            f'department_id={self.department_id}>'
        )


class StudentCourse(BaseModel):
    """
    Relation between Student and Course.

    Many-to-many relation.
    """

    __tablename__ = 'student_course'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    student_id = sa.Column(
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    score = sa.Column(
        sa.Float,
        default=0.0,
        nullable=False,
        server_default='0.0',
        doc='Sum of contests scores',
    )
    score_no_deadline = sa.Column(
        sa.Float,
        default=0.0,
        nullable=False,
        server_default='0.0',
        doc='Sum of contests scores no deadline',
    )
    contests_ok = sa.Column(
        sa.Integer, default=0, nullable=False, server_default='0'
    )
    is_ok = sa.Column(
        sa.Boolean, default=False, nullable=False, server_default='false'
    )
    is_ok_final = sa.Column(
        sa.Boolean, default=False, nullable=False, server_default='false'
    )

    allow_early_exam = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default='false',
        doc='Is student allowed to pass exam early',
    )

    def __repr__(self):  # type: ignore
        return (
            f'<StudentCourse student_id={self.student_id} '
            f'course_id={self.course_id}>'
        )


class StudentContest(BaseModel):
    """
    Relation between Student and Contest.

    Many-to-many relation.
    """

    __tablename__ = 'student_contest'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    contest_id = sa.Column(
        sa.ForeignKey('contest.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    student_id = sa.Column(
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    author_id = sa.Column(sa.Integer, nullable=False, unique=True)
    tasks_done = sa.Column(
        sa.Integer, default=0, nullable=False, server_default='0'
    )
    score = sa.Column(
        sa.Float,
        default=0.0,
        nullable=False,
        server_default='0.0',
        doc='Sum of tasks final scores',
    )
    score_no_deadline = sa.Column(
        sa.Float,
        default=0.0,
        nullable=False,
        server_default='0.0',
        doc='Sum of tasks best scores',
    )
    is_ok = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
        server_default='false',
        doc='Is ok for level Зачет автоматом',
    )
    is_ok_no_deadline = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
        server_default='false',
        doc='Is ok for level Допуск к зачету',
    )

    def __repr__(self):  # type: ignore
        return (
            f'<StudentContest student_id={self.student_id} '
            f'contest_id={self.contest_id}>'
        )


class StudentTask(BaseModel):
    """
    Relation between Student and Task.

    Many-to-many relation.
    """

    __tablename__ = 'student_task'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    contest_id = sa.Column(
        sa.ForeignKey('contest.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    task_id = sa.Column(
        sa.ForeignKey('task.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    student_id = sa.Column(
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    final_score = sa.Column(
        sa.Float,
        nullable=False,
        default=0,
        server_default='0.0',
        doc='Final score evaluated by final_score_evaluation_formula',
    )
    best_score_before_finish = sa.Column(
        sa.Float, nullable=False, default=0, server_default='0.0'
    )
    best_score_no_deadline = sa.Column(
        sa.Float, nullable=False, default=0, server_default='0.0'
    )
    is_done = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default='false',
    )
    best_score_before_finish_submission_id = sa.Column(
        UUID(as_uuid=True),
        nullable=True,
    )
    best_score_no_deadline_submission_id = sa.Column(
        UUID(as_uuid=True),
        nullable=True,
    )

    def __repr__(self):  # type: ignore
        return (
            f'<StudentContest student_id={self.student_id} '
            f'task_id={self.task_id}>'
        )


class StudentCourseLevels(BaseModel):
    __tablename__ = 'student_course_levels'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    student_id = sa.Column(
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    course_level_id = sa.Column(
        sa.ForeignKey('course_levels.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    is_ok = sa.Column(
        sa.Boolean, default=False, server_default='false', nullable=False
    )

    def __repr__(self):  # type: ignore
        return (
            f'<StudentCourseLevels student_id={self.student_id} '
            f'course_id={self.course_id} '
            f'course_level_id={self.course_level_id}>'
        )


class StudentContestLevels(BaseModel):
    __tablename__ = 'student_contest_levels'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    contest_id = sa.Column(
        sa.ForeignKey('contest.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    student_id = sa.Column(
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    contest_level_id = sa.Column(
        sa.ForeignKey('contest_levels.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    is_ok = sa.Column(
        sa.Boolean, default=False, server_default='false', nullable=False
    )

    def __repr__(self):  # type: ignore
        return (
            f'<StudentContestLevels student_id={self.student_id} '
            f'contest_id={self.contest_id} '
            f'contest_level_id={self.contest_level_id}>'
        )

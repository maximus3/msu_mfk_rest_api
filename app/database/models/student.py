import sqlalchemy as sa

from .base import BaseModel


class Student(BaseModel):
    """
    Student model in database.
    """

    __tablename__ = 'student'

    fio = sa.Column(sa.String)
    contest_login = sa.Column(sa.String, unique=True, index=True)
    token = sa.Column(sa.String, unique=True)


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
    score = sa.Column(sa.Float, nullable=False, server_default='0.0')
    contests_ok = sa.Column(sa.Integer, nullable=False, server_default='0')
    score_percent = sa.Column(sa.Float, nullable=False, server_default='0.0')
    contests_ok_percent = sa.Column(
        sa.Float, nullable=False, server_default='0.0'
    )
    is_ok = sa.Column(sa.Boolean, nullable=False, server_default='false')


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
    author_id = sa.Column(sa.Integer, nullable=True)
    tasks_done = sa.Column(sa.Integer, default=0, nullable=False)
    score = sa.Column(sa.Float, default=0.0, nullable=False)
    is_ok = sa.Column(sa.Boolean, default=False, nullable=False)

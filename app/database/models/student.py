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
    is_ok = sa.Column(sa.Boolean, default=False)


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
    tasks_done = sa.Column(sa.Integer)
    score = sa.Column(sa.Float)
    is_ok = sa.Column(sa.Boolean, default=False)

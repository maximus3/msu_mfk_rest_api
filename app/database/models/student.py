import sqlalchemy as sa

from .base import BaseModel


class Student(BaseModel):
    __tablename__ = 'student'

    fio = sa.Column(sa.String)
    contest_login = sa.Column(sa.String)
    token = sa.Column(sa.String)


class StudentDepartment(BaseModel):
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


class StudentContest(BaseModel):
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
    tasks_done = sa.Column(sa.Integer)
    is_ok = sa.Column(sa.Boolean, default=False)

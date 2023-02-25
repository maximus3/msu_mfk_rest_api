import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class Student(BaseModel):
    """
    Student model in database.
    """

    __tablename__ = 'student'

    fio = sa.Column(sa.String)
    contest_login = sa.Column(sa.String, unique=True, index=True)
    token = sa.Column(sa.String, unique=True)

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
    score = sa.Column(sa.Float, nullable=False, server_default='0.0')
    contests_ok = sa.Column(sa.Integer, nullable=False, server_default='0')
    score_percent = sa.Column(sa.Float, nullable=False, server_default='0.0')
    contests_ok_percent = sa.Column(
        sa.Float, nullable=False, server_default='0.0'
    )
    is_ok = sa.Column(sa.Boolean, nullable=False, server_default='false')
    is_ok_final = sa.Column(sa.Boolean, nullable=False, server_default='false')

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
    author_id = sa.Column(sa.Integer, nullable=True)
    tasks_done = sa.Column(sa.Integer, default=0, nullable=False)
    score = sa.Column(sa.Float, default=0.0, nullable=False)
    score_no_deadline = sa.Column(
        sa.Float, default=0.0, nullable=False, server_default='0.0'
    )
    is_ok = sa.Column(sa.Boolean, default=False, nullable=False)
    is_ok_no_deadline = sa.Column(
        sa.Boolean, default=False, nullable=False, server_default='false'
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
    final_score = sa.Column(sa.Float, nullable=False)
    no_deadline_score = sa.Column(sa.Float, nullable=False)
    is_done = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default='false',
    )
    best_submission_id = sa.Column(
        UUID(as_uuid=True),
        nullable=True,
    )
    best_no_deadline_submission_id = sa.Column(
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

# pylint: disable=duplicate-code

import sqlalchemy as sa

from .base import BaseModel


class Submission(BaseModel):
    __tablename__ = 'submission'

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
    student_task_id = sa.Column(
        sa.ForeignKey('student_task.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    author_id = sa.Column(sa.Integer, nullable=False)
    run_id = sa.Column(sa.Integer, nullable=False)
    verdict = sa.Column(sa.String, nullable=False)
    final_score = sa.Column(sa.Float, nullable=False)
    no_deadline_score = sa.Column(sa.Float, nullable=False)
    submission_link = sa.Column(sa.String, nullable=False)
    time_from_start = sa.Column(sa.Integer, nullable=False)
    submission_time = sa.Column(sa.DateTime, nullable=False)

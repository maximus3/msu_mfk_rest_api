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
    score_no_deadline = sa.Column(
        sa.Float, nullable=False, default=0, server_default='0.0'
    )
    score_before_finish = sa.Column(
        sa.Float, nullable=False, default=0, server_default='0.0'
    )
    submission_link = sa.Column(sa.String, nullable=False)
    submission_time = sa.Column(sa.DateTime, nullable=False)

    def __repr__(self):  # type: ignore
        return f'<Submission {self.run_id} author_id={self.author_id}>'

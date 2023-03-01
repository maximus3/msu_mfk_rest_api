# pylint: disable=duplicate-code

import sqlalchemy as sa

from .base import BaseModel


class Task(BaseModel):
    __tablename__ = 'task'

    contest_id = sa.Column(
        sa.ForeignKey('contest.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    yandex_task_id = sa.Column(
        sa.String,
        nullable=False,
        index=True,
    )
    name = sa.Column(
        sa.String,
        nullable=False,
    )
    alias = sa.Column(
        sa.String,
        nullable=False,
    )
    is_zero_ok = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default='false',
    )
    score_max = sa.Column(
        sa.Float, nullable=False, server_default='0.0', default=0.0
    )

    final_score_evaluation_formula = sa.Column(
        sa.String,
        nullable=False,
        default='{best_score_before_finish}',
        server_default='{best_score_before_finish}',
        doc='Default evaluation formula for tasks.'
        'Current available variables: '
        'best_score_before_finish, '
        'best_score_no_deadline',
    )

    def __repr__(self):  # type: ignore
        return f'<Task {self.yandex_task_id} contest_id={self.contest_id}>'

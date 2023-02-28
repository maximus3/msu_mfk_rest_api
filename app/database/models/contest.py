# pylint: disable=duplicate-code

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.schemas.contest import ContestTag

from .base import BaseModel
from .course import Course


class Contest(BaseModel):
    __tablename__ = 'contest'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    yandex_contest_id = sa.Column(
        sa.Integer, nullable=False, index=True, unique=True
    )
    deadline = sa.Column(sa.DateTime, nullable=True)
    lecture = sa.Column(sa.Integer, nullable=True)
    link = sa.Column(sa.String, unique=True)
    tasks_count = sa.Column(sa.Integer, nullable=True)
    score_max = sa.Column(sa.Float, nullable=True)
    levels = sa.Column(sa.JSON, nullable=True)
    tags = sa.Column(
        sa.ARRAY(sa.Enum(ContestTag)),
        nullable=False,
        default=[],
        server_default='{}',
    )
    name_format = sa.Column(
        sa.String,
        nullable=False,
        default='Лекция {lecture_num}',
        server_default='Лекция {lecture_num}',
    )

    default_final_score_evaluation_formula = sa.Column(
        sa.String,
        nullable=False,
        default='{best_score_before_finish}',
        server_default='{best_score_before_finish}',
        doc='Default evaluation formula for tasks.'
        'Current available variables: '
        'best_score_before_finish, '
        'best_score (include before)',
    )

    def __repr__(self):  # type: ignore
        return (
            f'<Contest {self.yandex_contest_id} (course_id={self.course_id})>'
        )

    def real_repr(self, session: Session) -> str:
        course_short_name = (
            session.query(Course)
            .where(Course.id == self.course_id)
            .first()
            .short_name
        )
        return f'<Contest {self.yandex_contest_id} ({course_short_name})>'


class ContestLevels(BaseModel):
    __tablename__ = 'contest_levels'

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
    level_name = sa.Column(sa.String, nullable=False)
    level_ok_method = sa.Column(
        sa.Enum('tasks_count', 'score_sum', name='contest_level_ok_method'),
        default='tasks_count',
        server_default='tasks_count',
        nullable=False,
    )
    count_method = sa.Column(
        sa.Enum('percent', 'absolute', name='contest_level_count_method'),
        default='percent',
        server_default='percent',
        nullable=False,
    )
    ok_threshold = sa.Column(
        sa.Float, default=100, server_default='100', nullable=False
    )
    include_after_deadline = sa.Column(
        sa.Boolean,
        default=False,
        server_default='false',
        nullable=False,
    )

    def __repr__(self):  # type: ignore
        return (
            f'<ContestLevel {self.level_name} '
            f'course_id={self.course_id} '
            f'contest_id={self.contest_id}>'
        )

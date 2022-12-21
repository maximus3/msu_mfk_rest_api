# pylint: disable=duplicate-code

import sqlalchemy as sa

from app.schemas.contest import ContestTag

from .base import BaseModel


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

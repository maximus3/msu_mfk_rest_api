# pylint: disable=duplicate-code

import sqlalchemy as sa

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
    deadline = sa.Column(sa.DateTime)
    lecture = sa.Column(sa.Integer)
    link = sa.Column(sa.String, unique=True)
    tasks_count = sa.Column(sa.Integer)
    tasks_need = sa.Column(sa.Integer)
    is_necessary = sa.Column(sa.Boolean)

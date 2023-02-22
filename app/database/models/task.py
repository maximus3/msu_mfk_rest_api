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

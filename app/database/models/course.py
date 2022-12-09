import sqlalchemy as sa

from .base import BaseModel


class Course(BaseModel):
    __tablename__ = 'course'

    name = sa.Column(sa.String, unique=True)
    short_name = sa.Column(sa.String, unique=True)
    channel_link = sa.Column(sa.String)
    chat_link = sa.Column(sa.String)
    lk_link = sa.Column(sa.String)
    ok_method = sa.Column(
        sa.Enum('contests_ok', 'score_sum', name='ok_method'),
        default='contests_ok',
        nullable=False,
    )
    ok_threshold_perc = sa.Column(sa.Integer, default=100, nullable=False)

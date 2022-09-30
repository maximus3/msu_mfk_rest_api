import sqlalchemy as sa

from .base import BaseModel


class Course(BaseModel):
    __tablename__ = 'course'

    name = sa.Column(sa.String, unique=True)
    short_name = sa.Column(sa.String, unique=True)
    channel_link = sa.Column(sa.String)
    chat_link = sa.Column(sa.String)
    lk_link = sa.Column(sa.String)

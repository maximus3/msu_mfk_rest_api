import sqlalchemy as sa

from .base import BaseModel


class Course(BaseModel):
    __tablename__ = 'course'

    name = sa.Column(sa.String, unique=True)
    short_name = sa.Column(sa.String, unique=True)
    channel_link = sa.Column(sa.String)
    chat_link = sa.Column(sa.String)
    lk_link = sa.Column(sa.String)
    score_max = sa.Column(
        sa.Float, nullable=False, server_default='0.0', default=0.0
    )
    contest_count = sa.Column(
        sa.Integer, nullable=False, server_default='0', default=0
    )
    ok_method = sa.Column(
        sa.Enum('contests_ok', 'score_sum', name='ok_method'),
        default='contests_ok',
        nullable=False,
    )
    ok_threshold_perc = sa.Column(sa.Integer, default=100, nullable=False)
    default_update_on = sa.Column(
        sa.Boolean, default=True, nullable=False, server_default='true'
    )
    is_open_registration = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
        server_default='false',
        doc='Is registration on this course open',
    )
    is_archive = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
        server_default='false',
        doc='Is course in archive (not show in api)',
    )


class CourseLevels(BaseModel):
    __tablename__ = 'course_levels'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    level_name = sa.Column(sa.String, nullable=False)
    level_ok_method = sa.Column(
        sa.Enum('contests_ok', 'score_sum', name='level_ok_method'),
        default='contests_ok',
        server_default='contests_ok',
        nullable=False,
    )
    contest_ok_level_name = sa.Column(sa.String, nullable=True)
    count_method = sa.Column(
        sa.Enum('percent', 'absolute', name='count_method'),
        default='percent',
        server_default='percent',
        nullable=False,
    )
    ok_threshold = sa.Column(
        sa.Float, default=100, server_default='100', nullable=False
    )

import sqlalchemy as sa

from .base import BaseModel


class Course(BaseModel):
    __tablename__ = 'course'

    name = sa.Column(
        sa.String,
        unique=True,
        nullable=False,
        doc='Course name.',
    )
    short_name = sa.Column(
        sa.String,
        unique=True,
        nullable=False,
        doc='Course short name.',
    )
    channel_link = sa.Column(
        sa.String,
        nullable=True,
        doc='Telegram channel link.',
    )  # TODO: rename tg_channel_link
    chat_link = sa.Column(
        sa.String,
        nullable=True,
        doc='Telegram chat link.',
    )  # TODO: rename tg_chat_link
    lk_link = sa.Column(
        sa.String,
        nullable=True,
        doc='Link for registration on lk.msu.ru for MFK students.',
    )

    info = sa.Column(
        sa.TEXT,
        nullable=True,
        doc='Course info.',
    )
    need_info_from_students = sa.Column(
        sa.JSON,
        nullable=True,
        doc='Info that students should provide. '
        'Format: {"data": [{'
        '"name": *info_name*, '
        '"help": *help_text*, '
        '"type": *regex/choose*, '
        '"regex": *regex if type is regex else null*, '
        '"choose": *list of options if type is choose else null*'
        '}]}',
    )

    is_active = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default='false',
        doc='Course activity status.',
    )
    is_open = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default='false',
        doc='Is course with open registration.',
    )
    code_word = sa.Column(
        sa.String,
        nullable=True,
        doc='Code word for not open courses.',
    )

    is_open_registration = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
        server_default='false',
        doc='Is registration on this course open',
    )
    register_start = sa.Column(
        sa.DateTime,
        nullable=True,
        doc='Start of registration.',
    )
    register_end = sa.Column(
        sa.DateTime,
        nullable=True,
        doc='End of registration.',
    )

    score_max = sa.Column(
        sa.Float, nullable=False, server_default='0.0', default=0.0
    )
    contest_count = sa.Column(
        sa.Integer, nullable=False, server_default='0', default=0
    )

    default_final_score_evaluation_formula = sa.Column(
        sa.String,
        nullable=False,
        default='{best_score_before_finish}',
        server_default='{best_score_before_finish}',
        doc='Default evaluation formula for tasks.'
        'Current available variables: '
        'best_score_before_finish, '
        'best_score_no_deadline',
    )

    is_archive = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
        server_default='false',
        doc='Is course in archive (not show in api)',
    )

    have_early_exam = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default='false',
        doc='Is course have early exam',
    )

    def __repr__(self) -> str:
        return f'<Course {self.short_name}>'


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
    level_info = sa.Column(
        sa.JSON,
        nullable=True,
        doc='Info about how to calculate level. '
        'Format: {"data": [{'
        '"level_ok_method": *contests_ok/score_sum*,'
        '"count_method": *percent/absolute*, '
        '"ok_threshold": *ok_threshold*, '
        '"contest_ok_level_name": *regex/choose*, '
        '"tags": [*list*, *of*, *tags*, *of*, *contests*]'
        '}]}',
    )

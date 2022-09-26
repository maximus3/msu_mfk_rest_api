import sqlalchemy as sa

from .base import BaseModel


class MFKUser(BaseModel):
    __tablename__ = 'mfk_user'

    fio = sa.Column(sa.String)
    department = sa.Column(sa.String)
    contest_login = sa.Column(sa.String)


class MFKUserCourse(BaseModel):
    __tablename__ = 'mfk_user_course'

    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    mfk_user_id = sa.Column(
        sa.ForeignKey('mfk_user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )


class MFKUserContest(BaseModel):
    __tablename__ = 'mfk_user_contest'

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
    mfk_user_id = sa.Column(
        sa.ForeignKey('mfk_user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    tasks_done = sa.Column(sa.Integer)
    is_ok = sa.Column(sa.Boolean, default=False)

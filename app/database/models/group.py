# pylint: disable=duplicate-code

import sqlalchemy as sa

from app.schemas import group as group_schemas

from .base import BaseModel


class Group(BaseModel):
    __tablename__ = 'group'

    name = sa.Column(
        sa.String,
        unique=True,
        nullable=False,
        doc='Group name.',
    )
    yandex_group_id = sa.Column(
        sa.Integer, unique=True, nullable=False, doc='Group ID from yandex.'
    )
    course_id = sa.Column(
        sa.ForeignKey('course.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    tags = sa.Column(
        sa.ARRAY(sa.Enum(group_schemas.GroupTag)),
        nullable=False,
        default=[],
        server_default='{}',
    )

    def __repr__(self):  # type: ignore
        return (
            f'<Group name={self.name} '
            f'yandex_group_id={self.yandex_group_id}>'
        )


class ContestGroup(BaseModel):
    """
    Relation between Contest and Group.

    Many-to-many relation.
    """

    __tablename__ = 'contest_group'

    group_id = sa.Column(
        sa.ForeignKey('group.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    contest_id = sa.Column(
        sa.ForeignKey('contest.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    def __repr__(self):  # type: ignore
        return (
            f'<ContestGroup contest_id={self.contest_id} '
            f'group_id={self.group_id}>'
        )


class StudentGroup(BaseModel):
    """
    Relation between Student and Group.

    Many-to-many relation.
    """

    __tablename__ = 'student_group'

    group_id = sa.Column(
        sa.ForeignKey('group.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    student_id = sa.Column(
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    def __repr__(self):  # type: ignore
        return (
            f'<StudentGroup student_id={self.student_id} '
            f'group_id={self.group_id}>'
        )

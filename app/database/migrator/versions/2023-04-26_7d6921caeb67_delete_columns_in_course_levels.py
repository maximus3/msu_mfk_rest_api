"""delete columns in course levels

Revision ID: 7d6921caeb67
Revises: 101c695271c3
Create Date: 2023-04-26 20:07:58.340454

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7d6921caeb67'
down_revision = '101c695271c3'
branch_labels = None
depends_on = None

types = [
    sa.Enum('contests_ok', 'score_sum', name='level_ok_method'),
    sa.Enum('percent', 'absolute', name='count_method'),
]


def upgrade() -> None:
    op.drop_column('course_levels', 'count_method')
    op.drop_column('course_levels', 'ok_threshold')
    op.drop_column('course_levels', 'contest_ok_level_name')
    op.drop_column('course_levels', 'level_ok_method')

    for type_ in types:
        type_.drop(op.get_bind(), checkfirst=False)


def downgrade() -> None:
    for type_ in types:
        type_.create(op.get_bind(), checkfirst=False)

    op.add_column(
        'course_levels',
        sa.Column(
            'level_ok_method',
            sa.Enum('contests_ok', 'score_sum', name='level_ok_method'),
            server_default=sa.text("'contests_ok'::level_ok_method"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'course_levels',
        sa.Column(
            'contest_ok_level_name',
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        'course_levels',
        sa.Column(
            'ok_threshold',
            postgresql.DOUBLE_PRECISION(precision=53),
            server_default=sa.text("'100'::double precision"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'course_levels',
        sa.Column(
            'count_method',
            sa.Enum('percent', 'absolute', name='count_method'),
            server_default=sa.text("'percent'::count_method"),
            autoincrement=False,
            nullable=False,
        ),
    )

"""course ok

Revision ID: 22c6121b977b
Revises: edccbc1f4833
Create Date: 2022-12-09 16:13:32.595835

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '22c6121b977b'
down_revision = 'edccbc1f4833'
branch_labels = None
depends_on = None


def upgrade() -> None:
    types = [
        sa.Enum('contests_ok', 'score_sum', name='ok_method'),
    ]
    for type_ in types:
        type_.create(op.get_bind(), checkfirst=False)

    op.add_column(
        'course',
        sa.Column(
            'ok_method',
            sa.Enum('contests_ok', 'score_sum', name='ok_method'),
            nullable=False,
            server_default='contests_ok',
        ),
    )
    op.add_column(
        'course',
        sa.Column(
            'ok_threshold_perc',
            sa.Integer(),
            nullable=False,
            server_default='100',
        ),
    )
    op.add_column(
        'student_course',
        sa.Column(
            'is_ok', sa.Boolean(), nullable=True, server_default='False'
        ),
    )


def downgrade() -> None:
    op.drop_column('student_course', 'is_ok')
    op.drop_column('course', 'ok_threshold_perc')
    op.drop_column('course', 'ok_method')

    types = [
        sa.Enum(name='ok_method'),
    ]
    for type_ in types:
        type_.drop(op.get_bind(), checkfirst=False)

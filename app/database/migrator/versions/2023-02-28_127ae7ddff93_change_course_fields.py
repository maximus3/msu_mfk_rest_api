"""change course fields

Revision ID: 127ae7ddff93
Revises: eb1428a3cff1
Create Date: 2023-02-28 11:26:14.184567

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '127ae7ddff93'
down_revision = 'eb1428a3cff1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('course', sa.Column('info', sa.TEXT(), nullable=True))
    op.add_column(
        'course',
        sa.Column('need_info_from_students', sa.JSON(), nullable=True),
    )
    op.add_column(
        'course',
        sa.Column(
            'is_active', sa.Boolean(), server_default='false', nullable=False
        ),
    )
    op.execute('UPDATE course SET is_active = TRUE WHERE is_archive IS FALSE')
    op.add_column(
        'course',
        sa.Column(
            'is_open', sa.Boolean(), server_default='false', nullable=False
        ),
    )
    op.add_column('course', sa.Column('code_word', sa.String(), nullable=True))
    op.add_column(
        'course', sa.Column('register_start', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'course', sa.Column('register_end', sa.DateTime(), nullable=True)
    )
    op.alter_column(
        'course', 'name', existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        'course', 'short_name', existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_column('course', 'default_update_on')
    op.drop_column('course', 'ok_threshold_perc')
    op.drop_column('course', 'ok_method')


def downgrade() -> None:
    op.add_column(
        'course',
        sa.Column(
            'ok_method',
            postgresql.ENUM('contests_ok', 'score_sum', name='ok_method'),
            server_default=sa.text("'contests_ok'::ok_method"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'course',
        sa.Column(
            'ok_threshold_perc',
            sa.INTEGER(),
            server_default=sa.text('100'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'course',
        sa.Column(
            'default_update_on',
            sa.BOOLEAN(),
            server_default=sa.text('true'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.alter_column(
        'course', 'short_name', existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        'course', 'name', existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_column('course', 'register_end')
    op.drop_column('course', 'register_start')
    op.drop_column('course', 'code_word')
    op.drop_column('course', 'is_open')
    op.drop_column('course', 'is_active')
    op.drop_column('course', 'need_info_from_students')
    op.drop_column('course', 'info')

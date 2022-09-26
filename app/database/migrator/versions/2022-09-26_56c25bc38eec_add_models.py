"""add models

Revision ID: 56c25bc38eec
Revises: 8bb82a9d9164
Create Date: 2022-09-26 20:23:16.484233

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '56c25bc38eec'
down_revision = '8bb82a9d9164'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'course',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('short_name', sa.String(), nullable=True),
        sa.Column('channel_link', sa.String(), nullable=True),
        sa.Column('chat_link', sa.String(), nullable=True),
        sa.Column('lk_link', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__course')),
        sa.UniqueConstraint('id', name=op.f('uq__course__id')),
        sa.UniqueConstraint('short_name', name=op.f('uq__course__short_name')),
    )
    op.create_table(
        'mfk_user',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('fio', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('contest_login', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__mfk_user')),
        sa.UniqueConstraint('id', name=op.f('uq__mfk_user__id')),
    )
    op.create_table(
        'contest',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('lecture', sa.Integer(), nullable=True),
        sa.Column('link', sa.String(), nullable=True),
        sa.Column('tasks_count', sa.Integer(), nullable=True),
        sa.Column('tasks_need', sa.Integer(), nullable=True),
        sa.Column('is_necessary', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__contest__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__contest')),
        sa.UniqueConstraint('id', name=op.f('uq__contest__id')),
    )
    op.create_index(
        op.f('ix__contest__course_id'), 'contest', ['course_id'], unique=False
    )
    op.create_table(
        'mfk_user_course',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'mfk_user_id', postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__mfk_user_course__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['mfk_user_id'],
            ['mfk_user.id'],
            name=op.f('fk__mfk_user_course__mfk_user_id__mfk_user'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__mfk_user_course')),
        sa.UniqueConstraint('id', name=op.f('uq__mfk_user_course__id')),
    )
    op.create_index(
        op.f('ix__mfk_user_course__course_id'),
        'mfk_user_course',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__mfk_user_course__mfk_user_id'),
        'mfk_user_course',
        ['mfk_user_id'],
        unique=False,
    )
    op.create_table(
        'mfk_user_contest',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column(
            'dt_created',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column(
            'dt_updated',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contest_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'mfk_user_id', postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column('tasks_done', sa.Integer(), nullable=True),
        sa.Column('is_ok', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['contest_id'],
            ['contest.id'],
            name=op.f('fk__mfk_user_contest__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__mfk_user_contest__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['mfk_user_id'],
            ['mfk_user.id'],
            name=op.f('fk__mfk_user_contest__mfk_user_id__mfk_user'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__mfk_user_contest')),
        sa.UniqueConstraint('id', name=op.f('uq__mfk_user_contest__id')),
    )
    op.create_index(
        op.f('ix__mfk_user_contest__contest_id'),
        'mfk_user_contest',
        ['contest_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__mfk_user_contest__course_id'),
        'mfk_user_contest',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__mfk_user_contest__mfk_user_id'),
        'mfk_user_contest',
        ['mfk_user_id'],
        unique=False,
    )
    op.create_unique_constraint(op.f('uq__user__id'), 'user', ['id'])


def downgrade() -> None:
    op.drop_constraint(op.f('uq__user__id'), 'user', type_='unique')
    op.drop_index(
        op.f('ix__mfk_user_contest__mfk_user_id'),
        table_name='mfk_user_contest',
    )
    op.drop_index(
        op.f('ix__mfk_user_contest__course_id'), table_name='mfk_user_contest'
    )
    op.drop_index(
        op.f('ix__mfk_user_contest__contest_id'), table_name='mfk_user_contest'
    )
    op.drop_table('mfk_user_contest')
    op.drop_index(
        op.f('ix__mfk_user_course__mfk_user_id'), table_name='mfk_user_course'
    )
    op.drop_index(
        op.f('ix__mfk_user_course__course_id'), table_name='mfk_user_course'
    )
    op.drop_table('mfk_user_course')
    op.drop_index(op.f('ix__contest__course_id'), table_name='contest')
    op.drop_table('contest')
    op.drop_table('mfk_user')
    op.drop_table('course')

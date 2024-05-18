"""init migration

Revision ID: eab58e734f0c
Revises:
Create Date: 2022-09-30 17:12:07.558343

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'eab58e734f0c'
down_revision = None
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
        sa.UniqueConstraint('name', name=op.f('uq__course__name')),
        sa.UniqueConstraint('short_name', name=op.f('uq__course__short_name')),
    )
    op.create_table(
        'department',
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
        sa.PrimaryKeyConstraint('id', name=op.f('pk__department')),
        sa.UniqueConstraint('id', name=op.f('uq__department__id')),
        sa.UniqueConstraint('name', name=op.f('uq__department__name')),
    )
    op.create_table(
        'student',
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
        sa.Column('contest_login', sa.String(), nullable=True),
        sa.Column('token', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student')),
        sa.UniqueConstraint('id', name=op.f('uq__student__id')),
    )
    op.create_table(
        'user',
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
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__user')),
        sa.UniqueConstraint('id', name=op.f('uq__user__id')),
    )
    op.create_index(
        op.f('ix__user__password'), 'user', ['password'], unique=False
    )
    op.create_index(
        op.f('ix__user__username'), 'user', ['username'], unique=True
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
        'student_course',
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
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__student_course__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__student_course__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student_course')),
        sa.UniqueConstraint('id', name=op.f('uq__student_course__id')),
    )
    op.create_index(
        op.f('ix__student_course__course_id'),
        'student_course',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_course__student_id'),
        'student_course',
        ['student_id'],
        unique=False,
    )
    op.create_table(
        'student_department',
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
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'department_id', postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['department_id'],
            ['department.id'],
            name=op.f('fk__student_department__department_id__department'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__student_department__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student_department')),
        sa.UniqueConstraint('id', name=op.f('uq__student_department__id')),
    )
    op.create_index(
        op.f('ix__student_department__department_id'),
        'student_department',
        ['department_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_department__student_id'),
        'student_department',
        ['student_id'],
        unique=False,
    )
    op.create_table(
        'student_contest',
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
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tasks_done', sa.Integer(), nullable=True),
        sa.Column('is_ok', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ['contest_id'],
            ['contest.id'],
            name=op.f('fk__student_contest__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__student_contest__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__student_contest__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student_contest')),
        sa.UniqueConstraint('id', name=op.f('uq__student_contest__id')),
    )
    op.create_index(
        op.f('ix__student_contest__contest_id'),
        'student_contest',
        ['contest_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_contest__course_id'),
        'student_contest',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_contest__student_id'),
        'student_contest',
        ['student_id'],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f('ix__student_contest__student_id'), table_name='student_contest'
    )
    op.drop_index(
        op.f('ix__student_contest__course_id'), table_name='student_contest'
    )
    op.drop_index(
        op.f('ix__student_contest__contest_id'), table_name='student_contest'
    )
    op.drop_table('student_contest')
    op.drop_index(
        op.f('ix__student_department__student_id'),
        table_name='student_department',
    )
    op.drop_index(
        op.f('ix__student_department__department_id'),
        table_name='student_department',
    )
    op.drop_table('student_department')
    op.drop_index(
        op.f('ix__student_course__student_id'), table_name='student_course'
    )
    op.drop_index(
        op.f('ix__student_course__course_id'), table_name='student_course'
    )
    op.drop_table('student_course')
    op.drop_index(op.f('ix__contest__course_id'), table_name='contest')
    op.drop_table('contest')
    op.drop_index(op.f('ix__user__username'), table_name='user')
    op.drop_index(op.f('ix__user__password'), table_name='user')
    op.drop_table('user')
    op.drop_table('student')
    op.drop_table('department')
    op.drop_table('course')

"""task

Revision ID: 1425cf1d90b0
Revises: 834c25260a81
Create Date: 2023-02-22 20:11:34.218807

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '1425cf1d90b0'
down_revision = '834c25260a81'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'task',
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
        sa.Column('contest_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('yandex_task_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('alias', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['contest_id'],
            ['contest.id'],
            name=op.f('fk__task__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__task')),
        sa.UniqueConstraint('id', name=op.f('uq__task__id')),
    )
    op.create_index(
        op.f('ix__task__contest_id'), 'task', ['contest_id'], unique=False
    )
    op.create_index(
        op.f('ix__task__yandex_task_id'),
        'task',
        ['yandex_task_id'],
        unique=False,
    )
    op.create_table(
        'student_task',
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
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('verdict', sa.String(), nullable=False),
        sa.Column('final_score', sa.Float(), nullable=False),
        sa.Column('no_deadline_score', sa.Float(), nullable=False),
        sa.Column('submission_link', sa.String(), nullable=False),
        sa.Column('time_from_start', sa.Integer(), nullable=False),
        sa.Column('submission_time', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['contest_id'],
            ['contest.id'],
            name=op.f('fk__student_task__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__student_task__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__student_task__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['task_id'],
            ['task.id'],
            name=op.f('fk__student_task__task_id__task'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student_task')),
        sa.UniqueConstraint('id', name=op.f('uq__student_task__id')),
    )
    op.create_index(
        op.f('ix__student_task__contest_id'),
        'student_task',
        ['contest_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_task__course_id'),
        'student_task',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_task__student_id'),
        'student_task',
        ['student_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_task__task_id'),
        'student_task',
        ['task_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix__student_task__task_id'), table_name='student_task')
    op.drop_index(
        op.f('ix__student_task__student_id'), table_name='student_task'
    )
    op.drop_index(
        op.f('ix__student_task__course_id'), table_name='student_task'
    )
    op.drop_index(
        op.f('ix__student_task__contest_id'), table_name='student_task'
    )
    op.drop_table('student_task')
    op.drop_index(op.f('ix__task__yandex_task_id'), table_name='task')
    op.drop_index(op.f('ix__task__contest_id'), table_name='task')
    op.drop_table('task')

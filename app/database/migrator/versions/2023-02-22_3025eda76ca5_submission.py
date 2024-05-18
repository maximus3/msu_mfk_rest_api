"""submission

Revision ID: 3025eda76ca5
Revises: 1425cf1d90b0
Create Date: 2023-02-22 22:51:27.070671

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '3025eda76ca5'
down_revision = '1425cf1d90b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'submission',
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
        sa.Column(
            'student_task_id', postgresql.UUID(as_uuid=True), nullable=False
        ),
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
            name=op.f('fk__submission__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__submission__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__submission__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_task_id'],
            ['student_task.id'],
            name=op.f('fk__submission__student_task_id__student_task'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['task_id'],
            ['task.id'],
            name=op.f('fk__submission__task_id__task'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__submission')),
        sa.UniqueConstraint('id', name=op.f('uq__submission__id')),
    )
    op.create_index(
        op.f('ix__submission__contest_id'),
        'submission',
        ['contest_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__submission__course_id'),
        'submission',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__submission__student_id'),
        'submission',
        ['student_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__submission__student_task_id'),
        'submission',
        ['student_task_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__submission__task_id'),
        'submission',
        ['task_id'],
        unique=False,
    )
    op.add_column(
        'student_task',
        sa.Column(
            'is_done', sa.Boolean(), server_default='false', nullable=False
        ),
    )
    op.add_column(
        'student_task',
        sa.Column(
            'best_submission_id', postgresql.UUID(as_uuid=True), nullable=True
        ),
    )
    op.create_unique_constraint(
        op.f('uq__student_task__id'), 'student_task', ['id']
    )
    op.drop_column('student_task', 'submission_time')
    op.drop_column('student_task', 'run_id')
    op.drop_column('student_task', 'verdict')
    op.drop_column('student_task', 'submission_link')
    op.drop_column('student_task', 'time_from_start')
    op.drop_column('student_task', 'author_id')
    op.add_column(
        'task',
        sa.Column(
            'is_zero_ok', sa.Boolean(), server_default='false', nullable=False
        ),
    )
    op.add_column(
        'task',
        sa.Column(
            'score_max', sa.Float(), server_default='0.0', nullable=False
        ),
    )
    op.create_unique_constraint(op.f('uq__task__id'), 'task', ['id'])


def downgrade() -> None:
    op.drop_constraint(op.f('uq__task__id'), 'task', type_='unique')
    op.drop_column('task', 'score_max')
    op.drop_column('task', 'is_zero_ok')
    op.add_column(
        'student_task',
        sa.Column(
            'author_id', sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        'student_task',
        sa.Column(
            'time_from_start',
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'student_task',
        sa.Column(
            'submission_link',
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        'student_task',
        sa.Column(
            'verdict', sa.VARCHAR(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        'student_task',
        sa.Column('run_id', sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.add_column(
        'student_task',
        sa.Column(
            'submission_time',
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_constraint(
        op.f('uq__student_task__id'), 'student_task', type_='unique'
    )
    op.drop_column('student_task', 'best_submission_id')
    op.drop_column('student_task', 'is_done')
    op.drop_index(op.f('ix__submission__task_id'), table_name='submission')
    op.drop_index(
        op.f('ix__submission__student_task_id'), table_name='submission'
    )
    op.drop_index(op.f('ix__submission__student_id'), table_name='submission')
    op.drop_index(op.f('ix__submission__course_id'), table_name='submission')
    op.drop_index(op.f('ix__submission__contest_id'), table_name='submission')
    op.drop_table('submission')

"""contest levels

Revision ID: 57b362bb3ba7
Revises: 2e510776406f
Create Date: 2023-02-22 20:02:02.835333

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '57b362bb3ba7'
down_revision = '2e510776406f'
branch_labels = None
depends_on = None

types = [
    sa.Enum('tasks_count', 'score_sum', name='contest_level_ok_method'),
    sa.Enum('percent', 'absolute', name='contest_level_count_method'),
]


def upgrade() -> None:
    op.create_table(
        'contest_levels',
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
        sa.Column('level_name', sa.String(), nullable=False),
        sa.Column(
            'level_ok_method',
            sa.Enum(
                'tasks_count', 'score_sum', name='contest_level_ok_method'
            ),
            server_default='tasks_count',
            nullable=False,
        ),
        sa.Column(
            'count_method',
            sa.Enum('percent', 'absolute', name='contest_level_count_method'),
            server_default='percent',
            nullable=False,
        ),
        sa.Column(
            'ok_threshold', sa.Float(), server_default='100', nullable=False
        ),
        sa.Column(
            'include_after_deadline',
            sa.Boolean(),
            server_default='false',
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['contest_id'],
            ['contest.id'],
            name=op.f('fk__contest_levels__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__contest_levels__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__contest_levels')),
        sa.UniqueConstraint('id', name=op.f('uq__contest_levels__id')),
    )
    op.create_index(
        op.f('ix__contest_levels__contest_id'),
        'contest_levels',
        ['contest_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__contest_levels__course_id'),
        'contest_levels',
        ['course_id'],
        unique=False,
    )
    op.create_table(
        'student_contest_levels',
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
        sa.Column(
            'contest_level_id', postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            'is_ok', sa.Boolean(), server_default='false', nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['contest_id'],
            ['contest.id'],
            name=op.f('fk__student_contest_levels__contest_id__contest'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['contest_level_id'],
            ['contest_levels.id'],
            name=op.f(
                'fk__student_contest_levels__contest_level_id__contest_levels'
            ),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__student_contest_levels__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__student_contest_levels__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student_contest_levels')),
        sa.UniqueConstraint('id', name=op.f('uq__student_contest_levels__id')),
    )
    op.create_index(
        op.f('ix__student_contest_levels__contest_id'),
        'student_contest_levels',
        ['contest_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_contest_levels__contest_level_id'),
        'student_contest_levels',
        ['contest_level_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_contest_levels__course_id'),
        'student_contest_levels',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_contest_levels__student_id'),
        'student_contest_levels',
        ['student_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix__student_contest_levels__student_id'),
        table_name='student_contest_levels',
    )
    op.drop_index(
        op.f('ix__student_contest_levels__course_id'),
        table_name='student_contest_levels',
    )
    op.drop_index(
        op.f('ix__student_contest_levels__contest_level_id'),
        table_name='student_contest_levels',
    )
    op.drop_index(
        op.f('ix__student_contest_levels__contest_id'),
        table_name='student_contest_levels',
    )
    op.drop_table('student_contest_levels')
    op.drop_index(
        op.f('ix__contest_levels__course_id'), table_name='contest_levels'
    )
    op.drop_index(
        op.f('ix__contest_levels__contest_id'), table_name='contest_levels'
    )
    op.drop_table('contest_levels')

    for type_ in types:
        type_.drop(op.get_bind(), checkfirst=False)

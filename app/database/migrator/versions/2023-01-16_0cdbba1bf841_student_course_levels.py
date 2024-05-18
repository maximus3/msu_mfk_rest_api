"""student course levels

Revision ID: 0cdbba1bf841
Revises: 94de9bbe6b97
Create Date: 2023-01-16 20:13:39.569548

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0cdbba1bf841'
down_revision = '94de9bbe6b97'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'student_course_levels',
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
        sa.Column(
            'course_level_id', postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            'is_ok', sa.Boolean(), server_default='false', nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__student_course_levels__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['course_level_id'],
            ['course_levels.id'],
            name=op.f(
                'fk__student_course_levels__course_level_id__course_levels'
            ),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__student_course_levels__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student_course_levels')),
        sa.UniqueConstraint('id', name=op.f('uq__student_course_levels__id')),
    )
    op.create_index(
        op.f('ix__student_course_levels__course_id'),
        'student_course_levels',
        ['course_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_course_levels__course_level_id'),
        'student_course_levels',
        ['course_level_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_course_levels__student_id'),
        'student_course_levels',
        ['student_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix__student_course_levels__student_id'),
        table_name='student_course_levels',
    )
    op.drop_index(
        op.f('ix__student_course_levels__course_level_id'),
        table_name='student_course_levels',
    )
    op.drop_index(
        op.f('ix__student_course_levels__course_id'),
        table_name='student_course_levels',
    )
    op.drop_table('student_course_levels')

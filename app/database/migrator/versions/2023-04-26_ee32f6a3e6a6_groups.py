"""groups

Revision ID: ee32f6a3e6a6
Revises: 35eeaa2743c5
Create Date: 2023-04-26 11:08:28.097138

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'ee32f6a3e6a6'
down_revision = '35eeaa2743c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'group',
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
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('yandex_group_id', sa.Integer(), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__group__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__group')),
        sa.UniqueConstraint('id', name=op.f('uq__group__id')),
        sa.UniqueConstraint('name', name=op.f('uq__group__name')),
        sa.UniqueConstraint(
            'yandex_group_id', name=op.f('uq__group__yandex_group_id')
        ),
    )
    op.create_index(
        op.f('ix__group__course_id'), 'group', ['course_id'], unique=False
    )
    op.create_table(
        'student_group',
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
        sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['group_id'],
            ['group.id'],
            name=op.f('fk__student_group__group_id__group'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['student_id'],
            ['student.id'],
            name=op.f('fk__student_group__student_id__student'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__student_group')),
        sa.UniqueConstraint('id', name=op.f('uq__student_group__id')),
    )
    op.create_index(
        op.f('ix__student_group__group_id'),
        'student_group',
        ['group_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix__student_group__student_id'),
        'student_group',
        ['student_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix__student_group__student_id'), table_name='student_group'
    )
    op.drop_index(
        op.f('ix__student_group__group_id'), table_name='student_group'
    )
    op.drop_table('student_group')
    op.drop_index(op.f('ix__group__course_id'), table_name='group')
    op.drop_table('group')

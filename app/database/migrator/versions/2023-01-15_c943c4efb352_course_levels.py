"""course levels

Revision ID: c943c4efb352
Revises: 8a4a8ee1b139
Create Date: 2023-01-15 10:26:13.312244

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c943c4efb352'
down_revision = '8a4a8ee1b139'
branch_labels = None
depends_on = None

types = [
    sa.Enum('contests_ok', 'score_sum', name='level_ok_method'),
    sa.Enum('percent', 'absolute', name='count_method'),
]


def upgrade() -> None:
    op.create_table(
        'course_levels',
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
            'level_ok_method',
            sa.Enum('contests_ok', 'score_sum', name='level_ok_method'),
            server_default='contests_ok',
            nullable=False,
        ),
        sa.Column(
            'count_method',
            sa.Enum('percent', 'absolute', name='count_method'),
            server_default='percent',
            nullable=False,
        ),
        sa.Column(
            'ok_threshold', sa.Float(), server_default='100', nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['course_id'],
            ['course.id'],
            name=op.f('fk__course_levels__course_id__course'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__course_levels')),
        sa.UniqueConstraint('id', name=op.f('uq__course_levels__id')),
    )
    op.create_index(
        op.f('ix__course_levels__course_id'),
        'course_levels',
        ['course_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix__course_levels__course_id'), table_name='course_levels'
    )
    op.drop_table('course_levels')

    for type_ in types:
        type_.drop(op.get_bind(), checkfirst=False)

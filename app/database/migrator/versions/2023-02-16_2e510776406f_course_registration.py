"""course registration

Revision ID: 2e510776406f
Revises: 0cdbba1bf841
Create Date: 2023-02-16 11:34:43.398221

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '2e510776406f'
down_revision = '0cdbba1bf841'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course',
        sa.Column(
            'is_open_registration',
            sa.Boolean(),
            server_default='false',
            nullable=False,
        ),
    )
    op.add_column(
        'course',
        sa.Column(
            'is_archive', sa.Boolean(), server_default='false', nullable=False
        ),
    )
    op.create_unique_constraint(
        op.f('uq__student_course_levels__id'), 'student_course_levels', ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__student_course_levels__id'),
        'student_course_levels',
        type_='unique',
    )
    op.drop_column('course', 'is_archive')
    op.drop_column('course', 'is_open_registration')

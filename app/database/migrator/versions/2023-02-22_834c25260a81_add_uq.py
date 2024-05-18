"""add uq

Revision ID: 834c25260a81
Revises: 57b362bb3ba7
Create Date: 2023-02-22 20:04:53.463772

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '834c25260a81'
down_revision = '57b362bb3ba7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        op.f('uq__contest_levels__id'), 'contest_levels', ['id']
    )
    op.create_unique_constraint(
        op.f('uq__student_contest_levels__id'),
        'student_contest_levels',
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__student_contest_levels__id'),
        'student_contest_levels',
        type_='unique',
    )
    op.drop_constraint(
        op.f('uq__contest_levels__id'), 'contest_levels', type_='unique'
    )

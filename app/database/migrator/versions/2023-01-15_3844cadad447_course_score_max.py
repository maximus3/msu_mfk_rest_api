"""course score max

Revision ID: 3844cadad447
Revises: c943c4efb352
Create Date: 2023-01-15 10:43:16.451788

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '3844cadad447'
down_revision = 'c943c4efb352'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course',
        sa.Column(
            'score_max', sa.Float(), server_default='0.0', nullable=False
        ),
    )
    op.create_unique_constraint(
        op.f('uq__course_levels__id'), 'course_levels', ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f('uq__course_levels__id'), 'course_levels', type_='unique'
    )
    op.drop_column('course', 'score_max')

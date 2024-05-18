"""course level add info

Revision ID: 94de9bbe6b97
Revises: 3844cadad447
Create Date: 2023-01-16 20:07:15.661301

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '94de9bbe6b97'
down_revision = '3844cadad447'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course_levels', sa.Column('level_name', sa.String(), nullable=False)
    )
    op.add_column(
        'course_levels',
        sa.Column('contest_ok_level_name', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('course_levels', 'contest_ok_level_name')
    op.drop_column('course_levels', 'level_name')

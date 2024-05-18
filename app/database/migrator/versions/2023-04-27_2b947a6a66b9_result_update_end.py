"""result_update_end

Revision ID: 2b947a6a66b9
Revises: 7d6921caeb67
Create Date: 2023-04-27 17:24:56.468480

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '2b947a6a66b9'
down_revision = '7d6921caeb67'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course_levels',
        sa.Column('result_update_end', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('course_levels', 'result_update_end')

"""level_info column

Revision ID: 101c695271c3
Revises: d70f50627143
Create Date: 2023-04-26 17:52:29.071897

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '101c695271c3'
down_revision = 'd70f50627143'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course_levels',
        sa.Column(
            'level_info', sa.JSON(), server_default='{}', nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column('course_levels', 'level_info')

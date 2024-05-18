"""ok no deadline

Revision ID: 8a4a8ee1b139
Revises: 8ab2035dca55
Create Date: 2022-12-22 14:11:19.402700

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '8a4a8ee1b139'
down_revision = '8ab2035dca55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student_contest',
        sa.Column(
            'is_ok_no_deadline',
            sa.Boolean(),
            server_default='false',
            nullable=False,
        ),
    )
    op.add_column(
        'student_course',
        sa.Column(
            'is_ok_final', sa.Boolean(), server_default='false', nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column('student_course', 'is_ok_final')
    op.drop_column('student_contest', 'is_ok_no_deadline')

"""final score server default

Revision ID: 7c8904d22ad5
Revises: df2011df54ff
Create Date: 2023-03-01 15:57:22.746007

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7c8904d22ad5'
down_revision = 'df2011df54ff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('student_task', 'final_score', server_default='0.0')


def downgrade() -> None:
    op.alter_column('student_task', 'final_score', server_default=None)

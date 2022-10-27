"""id in contest

Revision ID: edccbc1f4833
Revises: b992dbbba0e0
Create Date: 2022-10-27 23:31:57.383186

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'edccbc1f4833'
down_revision = 'b992dbbba0e0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student_contest', sa.Column('author_id', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('student_contest', 'author_id')

"""score in contests

Revision ID: b992dbbba0e0
Revises: 1374f4b563c3
Create Date: 2022-10-17 21:13:30.782010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b992dbbba0e0'
down_revision = '1374f4b563c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('contest', sa.Column('score_max', sa.Float(), nullable=True))
    op.add_column('contest', sa.Column('levels', sa.JSON(), nullable=True))
    op.drop_column('contest', 'tasks_need')
    op.add_column('student_contest', sa.Column('score', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('student_contest', 'score')
    op.add_column('contest', sa.Column('tasks_need', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('contest', 'levels')
    op.drop_column('contest', 'score_max')

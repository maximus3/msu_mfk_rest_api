"""rename score no deadlines

Revision ID: 81005070d65f
Revises: 7c8904d22ad5
Create Date: 2023-03-01 16:30:26.860692

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '81005070d65f'
down_revision = '7c8904d22ad5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'student_task', 'best_score', new_column_name='best_score_no_deadline'
    )
    op.alter_column('submission', 'score', new_column_name='score_no_deadline')


def downgrade() -> None:
    op.alter_column(
        'student_task', 'best_score_no_deadline', new_column_name='best_score'
    )
    op.alter_column('submission', 'score_no_deadline', new_column_name='score')

"""rename submission id

Revision ID: f745be74bd97
Revises: 81005070d65f
Create Date: 2023-03-01 16:37:07.632522

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f745be74bd97'
down_revision = '81005070d65f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'student_task',
        'best_score_submission_id',
        new_column_name='best_score_no_deadline_submission_id',
    )


def downgrade() -> None:
    op.alter_column(
        'student_task',
        'best_score_no_deadline_submission_id',
        new_column_name='best_score_submission_id',
    )

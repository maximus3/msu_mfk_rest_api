"""best_no_deadline_submission_id

Revision ID: eb1428a3cff1
Revises: 2569e4e1fdf6
Create Date: 2023-02-24 11:22:04.728949

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'eb1428a3cff1'
down_revision = '2569e4e1fdf6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'student_task',
        sa.Column(
            'best_no_deadline_submission_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column('student_task', 'best_no_deadline_submission_id')
